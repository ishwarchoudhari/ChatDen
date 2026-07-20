from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Block

User = get_user_model()


class BlockCreateSerializer(serializers.Serializer):
    """
    Validate the payload for creating a block relationship.

    Responsibilities:
    - Validate the request structure.
    - Resolve the target user from the provided primary key.
    - Do NOT enforce business rules.
    - Do NOT create Block objects.

    Business rules such as:
    - self-block prevention
    - duplicate block prevention
    - relationship policy

    remain in the View Layer and Relationship Service.
    """

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        help_text="UUID of the user to block.",
    )


class BlockSerializer(serializers.ModelSerializer):
    """
    Serialize a blocked relationship for API responses.
    """

    blocked_user_id = serializers.UUIDField(
        source="blocked.id",
        read_only=True,
    )

    blocked_username = serializers.CharField(
        source="blocked.username",
        read_only=True,
    )

    class Meta:
        model = Block
        fields = (
            "id",
            "blocked_user_id",
            "blocked_username",
            "created_at",
        )
        read_only_fields = fields

class PublicUserSerializer(serializers.ModelSerializer):
    """
    Serialize the public information of a user for discovery.

    Purpose
    -------
    This serializer is used by the Discovery API to expose only the
    information that is safe for other authenticated users to see.

    It intentionally does NOT expose any sensitive account data such as:

    - email
    - password
    - permissions
    - staff status
    - authentication fields

    Future phases may extend this serializer with additional public
    profile fields, but it should always remain limited to data that
    is intended for public visibility.
    """

    bio = serializers.CharField(
        source="profile.bio",
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "bio",
        )
        read_only_fields = fields        