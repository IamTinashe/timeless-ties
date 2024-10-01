from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from ..models import FamilyMember, Chiefdom, Village, Location
from django.contrib.auth import get_user_model

User = get_user_model()


class FamilyTreeAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.chiefdom = Chiefdom.objects.create(name="Chivero")
        self.village = Village.objects.create(name="Gumboreshumba", chiefdom=self.chiefdom)
        self.location = Location.objects.create(name="Harare")

        self.patriarch = FamilyMember.objects.create(
            first_name="John",
            last_name="Zvihwati",
            gender="M",
            date_of_birth="1950-01-01",
            user=self.user,
            chiefdom_of_origin=self.chiefdom,
            village_of_origin=self.village,
            current_location=self.location
        )

        self.matriarch = FamilyMember.objects.create(
            first_name="Jane",
            last_name="Zvihwati",
            gender="F",
            date_of_birth="1955-02-02",
            user=self.user,
            chiefdom_of_origin=self.chiefdom,
            village_of_origin=self.village,
            current_location=self.location
        )

        self.patriarch.spouses.add(self.matriarch)

        self.child = FamilyMember.objects.create(
            first_name="Alice",
            last_name="Zvihwati",
            gender="F",
            date_of_birth="1975-03-03",
            user=self.user,
            mother=self.matriarch,
            father=self.patriarch,
            chiefdom_of_origin=self.chiefdom,
            village_of_origin=self.village,
            current_location=self.location
        )

    def test_retrieve_family_tree(self):
        url = reverse('familytree-detail', kwargs={'clan_name': 'zvihwati'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # One root member
        root = response.data['results'][0]
        self.assertEqual(root['first_name'], "John")
        self.assertEqual(len(root['children']), 1)
        child = root['children'][0]
        self.assertEqual(child['first_name'], "Alice")
