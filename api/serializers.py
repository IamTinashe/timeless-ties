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
        chiefdom_name = validated_data.pop('chiefdom').strip()
        chiefdom, created = Chiefdom.objects.get_or_create(name__iexact=chiefdom_name)
        validated_data['chiefdom'] = chiefdom
        village_name = validated_data['name'].strip()

        # Perform case-insensitive search for Village
        village = Village.objects.filter(
            name__iexact=village_name,
            chiefdom=chiefdom
        ).first()

        if village:
            return village
        else:
            # Create Village with exact name (preserving case)
            return Village.objects.create(
                name=village_name,
                chiefdom=chiefdom
            )


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

        # Handle chiefdom_of_origin
        if chiefdom_name:
            chiefdom_name = chiefdom_name.strip()
            chiefdom, created = Chiefdom.objects.get_or_create(name__iexact=chiefdom_name)
            validated_data['chiefdom_of_origin'] = chiefdom
        else:
            chiefdom = None

        # Handle village_of_origin
        if village_data:
            village_name = village_data.get('name', '').strip()
            village_chiefdom_name = village_data.get('chiefdom', '').strip()

            # Determine the chiefdom to associate with the village
            if village_chiefdom_name:
                village_chiefdom, created = Chiefdom.objects.get_or_create(name__iexact=village_chiefdom_name)
            else:
                village_chiefdom = chiefdom  # Use chiefdom_of_origin if village chiefdom not provided

            if not village_chiefdom:
                raise serializers.ValidationError("Chiefdom is required to set village_of_origin.")

            # Perform case-insensitive search for Village
            village = Village.objects.filter(
                name__iexact=village_name,
                chiefdom=village_chiefdom
            ).first()

            if village:
                validated_data['village_of_origin'] = village
            else:
                # Create Village with exact name (preserving case)
                village = Village.objects.create(
                    name=village_name,
                    chiefdom=village_chiefdom
                )
                validated_data['village_of_origin'] = village

        # Handle current_location
        if location_name:
            location_name = location_name.strip()
            location, created = Location.objects.get_or_create(name__iexact=location_name)
            validated_data['current_location'] = location

        # Create the FamilyMember instance
        family_member = super().create(validated_data)
        family_member.spouses.set(spouses_data)

        return family_member

    def update(self, instance, validated_data):
        spouses_data = validated_data.pop('spouses', None)
        chiefdom_name = validated_data.pop('chiefdom_of_origin', None)
        village_data = validated_data.pop('village_of_origin', None)
        location_name = validated_data.pop('current_location', None)

        # Handle chiefdom_of_origin
        if chiefdom_name is not None:
            chiefdom_name = chiefdom_name.strip()
            chiefdom, created = Chiefdom.objects.get_or_create(name__iexact=chiefdom_name)
            validated_data['chiefdom_of_origin'] = chiefdom
        else:
            chiefdom = instance.chiefdom_of_origin

        # Handle village_of_origin
        if village_data is not None:
            village_name = village_data.get('name', '').strip()
            village_chiefdom_name = village_data.get('chiefdom', '').strip()

            # Determine the chiefdom to associate with the village
            if village_chiefdom_name:
                village_chiefdom, created = Chiefdom.objects.get_or_create(name__iexact=village_chiefdom_name)
            else:
                village_chiefdom = chiefdom  # Use chiefdom_of_origin if village chiefdom not provided

            if not village_chiefdom:
                raise serializers.ValidationError("Chiefdom is required to set village_of_origin.")

            # Perform case-insensitive search for Village
            village = Village.objects.filter(
                name__iexact=village_name,
                chiefdom=village_chiefdom
            ).first()

            if village:
                validated_data['village_of_origin'] = village
            else:
                # Create Village with exact name (preserving case)
                village = Village.objects.create(
                    name=village_name,
                    chiefdom=village_chiefdom
                )
                validated_data['village_of_origin'] = village

        # Handle current_location
        if location_name is not None:
            location_name = location_name.strip()
            location, created = Location.objects.get_or_create(name__iexact=location_name)
            validated_data['current_location'] = location

        # Update the FamilyMember instance
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
