from django.test import TestCase
from rest_framework.exceptions import ValidationError
from ..models import  FamilyMember, Chiefdom, Village, Location
from ..serializers import FamilyMemberSerializer


class FamilyMemberSerializerTest(TestCase):
    def setUp(self):
        self.chiefdom = Chiefdom.objects.create(name="Chivero")
        self.village = Village.objects.create(name="Gumboreshumba", chiefdom=self.chiefdom)
        self.location = Location.objects.create(name="Harare")

    def test_create_family_member(self):
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "gender": "M",
            "date_of_birth": "1980-01-01",
            "chiefdom_of_origin": "Chivero",
            "village_of_origin": {
                "name": "Gumboreshumba",
                "chiefdom": "Chivero"
            },
            "current_location": "Harare"
        }
        serializer = FamilyMemberSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        family_member = serializer.save()
        self.assertEqual(family_member.first_name, "John")
        self.assertEqual(family_member.last_name, "Doe")
        self.assertEqual(family_member.chiefdom_of_origin.name, "Chivero")
        self.assertEqual(family_member.village_of_origin.name, "Gumboreshumba")
        self.assertEqual(family_member.current_location.name, "Harare")

    def test_create_family_member_missing_chiefdom(self):
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "gender": "F",
            "date_of_birth": "1985-05-05",
            "village_of_origin": {
                "name": "UnknownVillage"
            },
            "current_location": "Harare"
        }
        serializer = FamilyMemberSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("chiefdom_of_origin", serializer.errors)
