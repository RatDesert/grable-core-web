import re
from django.contrib.auth import get_user_model
from django.core import exceptions, validators
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, fields

from .models import ActivateUserToken, ResetPasswordToken

# from .models import User

USERNAME_PATTERN = re.compile(r"^(?!.*\.\.)(?!.*\.$)[^\W][\w.]*$")
User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    # https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
    class Meta:
        model = User
        fields = ["username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def validate_username(self, value):
        if not re.match(USERNAME_PATTERN, value):
            raise serializers.ValidationError(
                (
                    "Username must contain only letters,"
                    "numbers, periods, and underscores."
                    "You can’t include symbols or"
                    "other punctuation marks as a part of your username."
                )
            )
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
            return value
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(list(e.messages))


class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password"]


class ActivateUserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivateUserToken
        fields = ["token"]


class ResetPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetPasswordToken
        fields = ["token", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value):
        try:
            validate_password(value)
        except exceptions.ValidationError as e:
            errors = dict(("password", list(e.messages)))
            raise serializers.ValidationError(errors)


class _ExistsSerailizer(serializers.Serializer):
    exists = fields.SerializerMethodField()

    def get_exists(self, obj):
        return User.objects.filter(**obj).exists()


class CheckEmailSerializer(_ExistsSerailizer):
    email = serializers.EmailField(max_length=254)


class CheckUsernameSeializer(_ExistsSerailizer):
    username = serializers.CharField(min_length=4, max_length=64)


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
