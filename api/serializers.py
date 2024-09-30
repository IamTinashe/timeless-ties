from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import (
    FamilyMember,
    Chiefdom,
    Village,
    Location,
    FamilyTree
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for CustomUser."""

    class Meta:
        model = User
        fields = ["id", "username", "email"]


class ChiefdomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chiefdom
        fields = ['id', 'name']


class VillageSerializer(serializers.ModelSerializer):
    chiefdom = serializers.CharField()

    class Meta:
        model = Village
        fields = ['id', 'name', 'chiefdom']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name']


class FamilyMemberSerializer(serializers.ModelSerializer):
    """Serializer for FamilyMember."""
    children_from_mother = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    children_from_father = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    mother = serializers.PrimaryKeyRelatedField(queryset=FamilyMember.objects.all(), allow_null=True)
    father = serializers.PrimaryKeyRelatedField(queryset=FamilyMember.objects.all(), allow_null=True)
    chiefdom_of_origin = serializers.CharField(allow_null=True, required=False)
    village_of_origin = VillageSerializer(allow_null=True, required=False)
    current_location = serializers.CharField(allow_null=True, required=False)
    spouses = serializers.PrimaryKeyRelatedField(
        queryset=FamilyMember.objects.all(),
        many=True,
        required=False
    )

    # Other fields and nested serializers as before...

    class Meta:
        model = FamilyMember
        fields = [
            'id',
            'first_name',
            'last_name',
            'gender',
            'date_of_birth',
            'date_of_death',
            'history',
            'user',
            'mother',
            'father',
            'spouses',
            'chiefdom_of_origin',
            'village_of_origin',
            'current_location',
            'children_from_mother',
            'children_from_father',
        ]
        read_only_fields = ['user']

    def create(self, validated_data):
        spouses_data = validated_data.pop('spouses', [])
        chiefdom_name = validated_data.pop('chiefdom_of_origin', None)
        village_data = validated_data.pop('village_of_origin', None)
        location_name = validated_data.pop('current_location', None)

        # Handle chiefdom
        if chiefdom_name:
            chiefdom, created = Chiefdom.objects.get_or_create(name=chiefdom_name)
            validated_data['chiefdom_of_origin'] = chiefdom
        else:
            chiefdom = None

        # Handle village
        if village_data:
            village_name = village_data.get('name')
            village_chiefdom_name = village_data.get('chiefdom', chiefdom_name)
            if village_chiefdom_name:
                village_chiefdom, created = Chiefdom.objects.get_or_create(name=village_chiefdom_name)
            else:
                village_chiefdom = chiefdom  # Use the chiefdom from chiefdom_of_origin if available

            if not village_chiefdom:
                raise serializers.ValidationError("Chiefdom is required to create a village.")

            village, created = Village.objects.get_or_create(
                name=village_name,
                chiefdom=village_chiefdom
            )
            validated_data['village_of_origin'] = village

        # Handle location
        if location_name:
            location, created = Location.objects.get_or_create(name=location_name)
            validated_data['current_location'] = location

        family_member = super().create(validated_data)
        family_member.spouses.set(spouses_data)

        return family_member

    def update(self, instance, validated_data):
        spouses_data = validated_data.pop('spouses', None)
        chiefdom_name = validated_data.pop('chiefdom_of_origin', None)
        village_data = validated_data.pop('village_of_origin', None)
        location_name = validated_data.pop('current_location', None)

        # Handle chiefdom
        if chiefdom_name is not None:
            chiefdom, created = Chiefdom.objects.get_or_create(name=chiefdom_name)
            validated_data['chiefdom_of_origin'] = chiefdom
        else:
            chiefdom = instance.chiefdom_of_origin

        # Handle village
        if village_data is not None:
            village_name = village_data.get('name')
            village_chiefdom_name = village_data.get('chiefdom')
            if village_chiefdom_name:
                village_chiefdom, created = Chiefdom.objects.get_or_create(name=village_chiefdom_name)
            else:
                village_chiefdom = chiefdom  # Use the chiefdom from chiefdom_of_origin if available

            if not village_chiefdom:
                raise serializers.ValidationError("Chiefdom is required to create a village.")

            village, created = Village.objects.get_or_create(
                name=village_name,
                chiefdom=village_chiefdom
            )
            validated_data['village_of_origin'] = village

        # Handle location
        if location_name is not None:
            location, created = Location.objects.get_or_create(name=location_name)
            validated_data['current_location'] = location

        family_member = super().update(instance, validated_data)
        if spouses_data is not None:
            family_member.spouses.set(spouses_data)
        return family_member


class FamilyTreeSerializer(serializers.ModelSerializer):
    """Serializer for FamilyTree."""

    members = FamilyMemberSerializer(many=True, read_only=True)

    class Meta:
        model = FamilyTree
        fields = ["id", "name", "description", "owner", "members"]
        read_only_fields = ["owner"]
