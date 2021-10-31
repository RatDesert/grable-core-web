from typing import Optional, Tuple
from jwt import exceptions
from django.middleware.csrf import CsrfViewMiddleware
from django.core import signing
from django.conf import settings
from rest_framework import authentication, exceptions
from .models import RefreshSession, User
from .utils import AccessJWT, JWT


class CSRFCheck(CsrfViewMiddleware):
    def _reject(self, request, reason):
        # Return the failure reason instead of an HttpResponse
        raise exceptions.PermissionDenied(f"CSRF Failed: {reason}")


class JWTAuthentication(authentication.BaseAuthentication):
    def enforce_csrf(self, request):
        csrf_check = CSRFCheck()
        csrf_check.process_request(request)
        reason = csrf_check.process_view(request, None, (), {})
        if reason:
            raise exceptions.PermissionDenied(f"CSRF Failed: {reason}")

    def authenticate(self, request) -> Tuple[User, JWT]:
        # self.enforce_csrf(request)
        token = self.get_jwt(request)

        if token is None:
            return None

        jwt = self.verify_jwt(token)
        user = self.get_user(jwt)
        return user, jwt

    def get_jwt(self, request) -> Optional[str]:
        return request.COOKIES.get(settings.AUTH_ACCESS_COOKIE_NAME, None)

    def verify_jwt(self, token: str) -> JWT:
        try:
            jwt = AccessJWT().decode(token)

        except exceptions.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed(
                "Access JWT has expired", code="access_token_expired"
            )
        except (exceptions.InvalidTokenError):
            raise exceptions.AuthenticationFailed(
                "Access JWT is invalid ", code="access_token_not_valid"
            )

        if jwt.payload.token_type != "access":
            raise exceptions.AuthenticationFailed(
                "Access JWT is invalid", code="access_token_not_valid"
            )

        return jwt

    def get_user(self, jwt: JWT) -> User:
        # TODO: return JWTUser(AnonymousUser) class
        user_id = jwt.payload.user_id

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                "User does not exist", code="user_not_found"
            )

        if not user.is_active:
            raise exceptions.AuthenticationFailed(
                "User is inactive", code="user_inactive"
            )

        return user

    def authenticate_header(self, request):
        # in case of missing auth cookie
        return 'Cookie realm="api"'


class RefreshAuthentication(authentication.BaseAuthentication):
    def enforce_csrf(self, request) -> None:
        csrf_check = CSRFCheck()
        csrf_check.process_request(request)
        reason = csrf_check.process_view(request, None, (), {})

        if reason:
            raise exceptions.PermissionDenied(f"CSRF Failed: {reason}")

    def authenticate(self, request) -> Tuple[User, RefreshSession]:
        # self.enforce_csrf(request)

        try:
            session_key = request.get_signed_cookie(
                settings.AUTH_REFRESH_COOKIE_NAME,
                salt=settings.AUTH_REFRESH_COOKIE_SALT,
                max_age=settings.AUTH_REFRESH_MAX_AGE_SEC,
            )
        except (KeyError, signing.BadSignature, signing.SignatureExpired):
            return None

        user = self.get_user(session_key)
        refresh_session = user.refresh_sessions.filter(session_key=session_key)[0]

        return user, refresh_session

    def get_user(self, session_key: str) -> User:
        try:
            user = User.objects.prefetch_related("refresh_sessions").get(
                refresh_sessions__session_key=session_key
            )
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                "User does not exist", code="user_not_found"
            )

        if not user.is_active:
            raise exceptions.AuthenticationFailed(
                "User is inactive", code="user_inactive"
            )

        return user

    def authenticate_header(self, request) -> str:
        return 'Cookie realm="api/auth"'
