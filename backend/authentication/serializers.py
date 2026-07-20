from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model

class LoginSerializer(serializers.Serializer):
    """
    Validate user login credentials.
    """

    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        email = attrs.get("email", "").strip().lower()
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid email or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This account is inactive."
            )

        attrs["authenticated_user"] = user

        return attrs
    

from rest_framework_simplejwt.serializers import (
    TokenRefreshSerializer,
)


class RefreshSerializer(TokenRefreshSerializer):
    """
    Validate and rotate refresh tokens using SimpleJWT's
    built-in implementation.
    """

    pass

class LogoutSerializer(serializers.Serializer):
    """
    Blacklist a refresh token.
    """

    refresh = serializers.CharField(write_only=True)

    def save(self, **kwargs):
        refresh_token = self.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

        except TokenError:
            raise serializers.ValidationError(
                {
                    "refresh": [
                        "Invalid or expired refresh token."
                    ]
                }
            )
        
class UserSerializer(serializers.ModelSerializer):
    """
    Serialize the authenticated user.
    """

    class Meta:
        model = get_user_model()

        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
        )

        read_only_fields = fields        