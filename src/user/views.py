from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import mixins, serializers, viewsets, status, permissions, views
from rest_framework.decorators import action, api_view

from .serializers import (
    UserCreateSerializer,
    CheckUsernameSeializer,
    CheckEmailSerializer,
    ActivateUserTokenSerializer,
    UserRetrieveSerializer,
    EmailSerializer,
    ResetPasswordSerializer,
)
from .utils import (
    get_user_activation_url,
    get_password_reset_url,
    send_activate_account_email,
    send_reset_password_email,
)
from .exceptions import EmailTokenNotValid
from .throttle import (
    CheckUserAtributesThrottle,
    RegistrationThrottle,
    ActivateAccountThrottle,
    ResetPasswordThrottle,
)
from .models import ActivateUserToken, ResetPasswordToken, generate_token64
from jwt_auth import authentication

User = get_user_model()


class RegisterViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Registers the user."""

    serializer_action_classes = {
        "create": UserCreateSerializer,
    }

    throttle_action_classes = {"create": [RegistrationThrottle]}

    def get_serializer_class(self):
        return self.serializer_action_classes.get(self.action)

    def get_throttles(self):
        throttles = self.throttle_action_classes.get(self.action, [])
        return [throttle() for throttle in throttles]

    def perform_create(self, serializer):
        user = serializer.save()
        token, _ = ActivateUserToken.objects.update_or_create(
            user=user, defaults={"token": generate_token64()}
        )
        activation_url = get_user_activation_url(token)
        send_activate_account_email(user, activation_url, self.request)

    def create(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            status=status.HTTP_201_CREATED,
            data={"detail": "Please check email to confirm your registration."},
        )

    @action(
        detail=False, methods=["GET"], throttle_classes=[CheckUserAtributesThrottle]
    )
    def check_username(self, request):
        username = request.query_params.get("username", None)
        serializer = CheckUsernameSeializer(data={"username": username})
        serializer.is_valid(raise_exception=True)

        if serializer.data.get("exists"):
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.data, status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=False, methods=["GET"], throttle_classes=[CheckUserAtributesThrottle]
    )
    def check_email(self, request):
        email = request.query_params.get("email", None)
        serializer = CheckEmailSerializer(data={"email": email})
        serializer.is_valid(raise_exception=True)

        if serializer.data.get("exists"):
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.data, status=status.HTTP_404_NOT_FOUND)

    @action(
        methods=["POST"],
        detail=False,
        throttle_classes=[ActivateAccountThrottle],
    )
    def confirm_email(self, request):
        serializer = ActivateUserTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            ActivateUserToken.objects.activate_user(**serializer.validated_data)
            return Response(
                {"message": "Token not valid."},
                status=status.HTTP_200_OK,
            )
        except ActivateUserToken.DoesNotExist:
            return Response(
                {"message": "Token not valid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["POST"], throttle_classes=[ActivateAccountThrottle])
    def send_confirm_email(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            data = serializer.data
            email = data["email"]
            user = User.objects.get(email=email)

            if user.is_active:
                return Response(
                    {"message": "User account is already activated"},
                    status=status.HTTP_409_CONFLICT,
                )

            token, _ = ActivateUserToken.objects.update_or_create(
                user=user,
                defaults={"token": generate_token64()},
            )
            activation_url = get_user_activation_url(token)
            send_activate_account_email(user, activation_url, request)
        except User.DoesNotExist:
            pass

        return Response(
            data={
                "message": (
                    "If a matching account was found "
                    f"an email was sent to {email} "
                    "to allow you to activate your account."
                )
            },
            status=status.HTTP_202_ACCEPTED,
        )


class UserView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.JWTAuthentication]

    def get(self, request):
        serializer = UserRetrieveSerializer(request.user)
        return Response(serializer.data)


@api_view(["POST"])
def forgot_password(request):
    serializer = EmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.data
    email = data["email"]

    try:
        user = User.objects.get(email=email)

        if not user.is_active:
            return Response(
                {"message": "User account not active."},
                status=status.HTTP_409_CONFLICT,
            )

        token, _ = ResetPasswordToken.objects.update_or_create(
            user=user, defaults={"token": generate_token64()}
        )
        activation_url = get_password_reset_url(user, token)
        send_reset_password_email(user, activation_url, request)
    except User.DoesNotExist:
        pass

    return Response(
        data={
            "message": (
                "If a matching account was found"
                f"an email was sent to {email}"
                "to allow you to reset your password."
            )
        },
        status=status.HTTP_202_ACCEPTED,
    )


@api_view(["POST"])
def reset_password(request):
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.data
    token, password = data["token"], data["password"]

    try:
        User.objects.change_password(token, password)
        return Response(status=status.HTTP_204_NO_CONTENT)
        # notify user
    except User.DoesNotExist:
        return Response(
            data={"token": "Not valid."}, status=status.HTTP_400_BAD_REQUEST
        )
