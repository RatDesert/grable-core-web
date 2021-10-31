from datetime import datetime
from dataclasses import field, dataclass
from uuid import uuid4, UUID
import jwt
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from .models import RefreshSession

User = get_user_model()


@dataclass(frozen=True)
class JWTPayload:
    user_id: str | int
    token_type: str
    exp: datetime
    jti: UUID

    @property
    def exp_iso(self) -> str:
        return self.exp.strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class AccessJWTPayload(JWTPayload):
    token_type: str = "access"
    exp: datetime = field(
        default_factory=lambda: timezone.now() + settings.AUTH_ACCESS_MAX_AGE_SEC
    )
    jti: UUID = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class JWT:
    payload: AccessJWTPayload
    token: str


class AccessJWT:
    def __init__(self, algorithm="HS256"):
        self.algorithm = algorithm

    def encode(self, user: User) -> JWT:
        payload = AccessJWTPayload(user.pk)
        token = jwt.encode(
            payload.__dict__.copy(),
            settings.AUTH_ACCESS_JWT_SIGNING_KEY,
            algorithm=self.algorithm,
        )
        return JWT(payload, token)

    def decode(self, token: str) -> JWT:
        payload = jwt.decode(
            token,
            settings.AUTH_ACCESS_JWT_SIGNING_KEY,
            algorithms=[self.algorithm],
            options={"verify_exp": True},
        )
        payload = AccessJWTPayload(**payload)
        return JWT(payload, token)


def delete_user_sessions(user: User) -> QuerySet[RefreshSession]:
    return RefreshSession.objects.filter(user=user).delete()
