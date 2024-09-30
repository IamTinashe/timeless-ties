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

    def create(self, validated_data):
        chiefdom_name = validated_data.pop('chiefdom')
        chiefdom, created = Chiefdom.objects.get_or_create(name__iexact=chiefdom_name)
        validated_data['chiefdom'] = chiefdom
        village, created = Village.objects.get_or_create(
            name__iexact=validated_data['name'],
            chiefdom=chiefdom,
            defaults={'name': validated_data['name']}
        )
        return village



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
        village_name = validated_data.pop('village_of_origin', None)
        location_name = validated_data.pop('current_location', None)

        if chiefdom_name:
            chiefdom, created = Chiefdom.objects.get_or_create(name__iexact=chiefdom_name)
            validated_data['chiefdom_of_origin'] = chiefdom

            # Handle village_of_origin
        if village_name:
            if 'chiefdom_of_origin' in validated_data:
                chiefdom = validated_data['chiefdom_of_origin']
            else:
                chiefdom = None
            if not chiefdom:
                raise serializers.ValidationError("Chiefdom of origin is required to set village_of_origin.")
            village, created = Village.objects.get_or_create(
                name__iexact=village_name,
                chiefdom=chiefdom
            )
            validated_data['village_of_origin'] = village

            # Handle current_location
        if location_name:
            location, created = Location.objects.get_or_create(name__iexact=location_name)
            validated_data['current_location'] = location

        family_member = super().create(validated_data)
        family_member.spouses.set(spouses_data)

        return family_member

    def update(self, instance, validated_data):
        spouses_data = validated_data.pop('spouses', None)
        chiefdom_name = validated_data.pop('chiefdom_of_origin', None)
        village_name = validated_data.pop('village_of_origin', None)
        location_name = validated_data.pop('current_location', None)

        # Handle chiefdom_of_origin
        if chiefdom_name is not None:
            chiefdom, created = Chiefdom.objects.get_or_create(name__iexact=chiefdom_name)
            validated_data['chiefdom_of_origin'] = chiefdom

        # Handle village_of_origin
        if village_name is not None:
            if 'chiefdom_of_origin' in validated_data:
                chiefdom = validated_data['chiefdom_of_origin']
            else:
                chiefdom = instance.chiefdom_of_origin
            if not chiefdom:
                raise serializers.ValidationError("Chiefdom of origin is required to set village_of_origin.")
            village, created = Village.objects.get_or_create(
                name__iexact=village_name,
                chiefdom=chiefdom
            )
            validated_data['village_of_origin'] = village

        # Handle current_location
        if location_name is not None:
            location, created = Location.objects.get_or_create(name__iexact=location_name)
            validated_data['current_location'] = location

        family_member = super().update(instance, validated_data)

        if spouses_data is not None:
            family_member.spouses.set(spouses_data)

        return family_member

    def validate(self, data):
        if self.instance:
            # Prevent self as mother or father
            if data.get('mother') and data['mother'] == self.instance:
                raise serializers.ValidationError("A family member cannot be their own mother.")
            if data.get('father') and data['father'] == self.instance:
                raise serializers.ValidationError("A family member cannot be their own father.")
            # Prevent self as spouse
            if 'spouses' in data and self.instance in data['spouses']:
                raise serializers.ValidationError("A family member cannot be their own spouse.")
        return data


class FamilyTreeSerializer(serializers.ModelSerializer):
    """Serializer for FamilyTree."""

    members = FamilyMemberSerializer(many=True, read_only=True)

    class Meta:
        model = FamilyTree
        fields = ["id", "name", "description", "owner", "members"]
        read_only_fields = ["owner"]

