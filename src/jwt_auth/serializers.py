from django.contrib.auth import authenticate
from rest_framework import serializers, fields
from rest_framework.exceptions import ValidationError
from .models import RefreshSession


class LoginSerializer(serializers.Serializer):
    username = fields.CharField(write_only=True, max_length=64)
    password = fields.CharField(write_only=True, max_length=64)

    def validate(self, data):
        username, password = data.pop("username"), data.pop("password")
        user = authenticate(username=username, password=password)

        if user is None or user.is_active is False:
            raise ValidationError("Incorrect username or password.")
        self.context["request"].user = user

        return data


class RefreshSessionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefreshSession
        fields = ["expires_at", "http_user_agent", "remote_addr", "remote_host"]
