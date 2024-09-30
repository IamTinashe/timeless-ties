from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import FamilyMember

User = get_user_model()


class FamilyMemberModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")

    def test_create_family_member(self):
        member = FamilyMember.objects.create(
            first_name="John", last_name="Doe", user=self.user
        )
        self.assertEqual(member.first_name, "John")
        self.assertEqual(member.user.username, "testuser")
