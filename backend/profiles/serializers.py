from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serialize a user's profile.
    """

    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )

    username = serializers.CharField(
        source="user.username",
        read_only=True,
    )

    class Meta:
        model = Profile

        fields = (
            "email",
            "username",
            "bio",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "email",
            "username",
            "created_at",
            "updated_at",
        )
    def update(self, instance, validated_data):
        """
        Update editable profile fields.
        """

        if "bio" in validated_data:
            bio = validated_data["bio"]

            if bio != instance.bio:
                instance.bio = bio
                instance.save(update_fields=["bio", "updated_at"])

        return instance