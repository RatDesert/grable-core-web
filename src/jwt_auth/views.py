from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator, decorator_from_middleware
from rest_framework.decorators import (
    api_view,
    throttle_classes,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from .utils import AccessJWT
from .throttle import RefreshThrottle
from .serializers import LoginSerializer, RefreshSessionListSerializer
from .authentication import RefreshAuthentication, CSRFCheck, JWTAuthentication
from .models import RefreshSession, get_session_key, get_session_expire_date

csrf_protect = decorator_from_middleware(CSRFCheck)


class LoginView(APIView):

    # @method_decorator(csrf_protect)
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            user = request.user
            http_user_agent = request.headers.get("User-Agent", None)
            remote_addr = request.META.get("REMOTE_ADDR", None)
            remote_host = request.META.get("REMOTE_HOST", None)

            refresh_session = RefreshSession.objects.create(
                user=user,
                http_user_agent=http_user_agent,
                remote_addr=remote_addr,
                remote_host=remote_host,
            )

            jwt = AccessJWT().encode(user)
            data = {
                "access_cookie_expiration": jwt.payload.exp_iso,
                "refresh_cookie_expiration": refresh_session.expires_at,
            }

            response = Response(data)
            response.set_cookie(
                settings.AUTH_ACCESS_COOKIE_NAME,
                value=jwt.token,
                path=settings.AUTH_ACCESS_COOKIE_SCOPE,
                expires=jwt.payload.exp,
                httponly=True,
            )

            response.set_signed_cookie(
                settings.AUTH_REFRESH_COOKIE_NAME,
                path=settings.AUTH_REFRESH_COOKIE_SCOPE,
                salt=settings.AUTH_REFRESH_COOKIE_SALT,
                value=refresh_session.session_key,
                expires=refresh_session.expires_at,
                httponly=True,
            )
            return response

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(ensure_csrf_cookie)
    # TODO this endpoint must return static login form with csrf cookie
    def get(self, request):
        return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
@throttle_classes([RefreshThrottle])
@authentication_classes((RefreshAuthentication,))
@permission_classes((permissions.IsAuthenticated,))
def refresh_tokens(request):
    user = request.user
    refresh_session = request.auth
    refresh_session.http_user_agent = request.headers.get("User-Agent", None)
    refresh_session.remote_addr = request.META.get("REMOTE_ADDR", None)
    refresh_session.remote_host = request.META.get("REMOTE_HOST", None)

    refresh_session.session_key = get_session_key()
    refresh_session.expires_at = get_session_expire_date()
    refresh_session.save()

    jwt = AccessJWT().encode(user)
    data = {
        "access_cookie_expiration": jwt.payload.exp_iso,
        "refresh_cookie_expiration": refresh_session.expires_at,
    }

    response = Response(data)
    response.set_cookie(
        settings.AUTH_ACCESS_COOKIE_NAME,
        value=jwt.token,
        path=settings.AUTH_ACCESS_COOKIE_SCOPE,
        expires=jwt.payload.exp,
        httponly=True,
    )
    response.set_signed_cookie(
        settings.AUTH_REFRESH_COOKIE_NAME,
        path=settings.AUTH_REFRESH_COOKIE_SCOPE,
        salt=settings.AUTH_REFRESH_COOKIE_SALT,
        value=refresh_session.session_key,
        expires=refresh_session.expires_at,
        httponly=True,
    )
    return response


@api_view(["POST"])
@authentication_classes((RefreshAuthentication,))
@permission_classes((permissions.IsAuthenticated,))
def logout(request):
    refresh_session = request.auth
    refresh_session.delete()
    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie(
        settings.AUTH_ACCESS_COOKIE_NAME, path=settings.AUTH_ACCESS_COOKIE_SCOPE
    )
    response.delete_cookie(
        settings.AUTH_REFRESH_COOKIE_NAME, path=settings.AUTH_REFRESH_COOKIE_SCOPE
    )
    return response


@api_view(["GET"])
@authentication_classes((JWTAuthentication,))
@permission_classes((permissions.IsAuthenticated,))
def sessions(request):
    user = request.user
    sessions = RefreshSession.objects.filter(user=user)
    serializer = RefreshSessionListSerializer(sessions, many=True)
    return Response(serializer.data)
