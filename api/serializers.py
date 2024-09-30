from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import FamilyMember, FamilyTree

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for CustomUser."""

    class Meta:
        model = User
        fields = ["id", "username", "email"]


class FamilyMemberSerializer(serializers.ModelSerializer):
    """Serializer for FamilyMember."""

    children = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = FamilyMember
        fields = [
            "id",
            "first_name",
            "last_name",
            "date_of_birth",
            "date_of_death",
            "bio",
            "user",
            "parent",
            "children",
        ]
        read_only_fields = ["user"]


class FamilyTreeSerializer(serializers.ModelSerializer):
    """Serializer for FamilyTree."""

    members = FamilyMemberSerializer(many=True, read_only=True)

    class Meta:
        model = FamilyTree
        fields = ["id", "name", "description", "owner", "members"]
        read_only_fields = ["owner"]
