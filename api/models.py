from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model."""

    # Add additional fields if needed, e.g.,
    # middle_name = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.username


class GenderChoices(models.TextChoices):
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'
    OTHER = 'O', 'Other'


class FamilyMember(models.Model):
    """Model representing a family member."""

    first_name = models.CharField(null=True, max_length=50)
    last_name = models.CharField(null=True, max_length=50)
    gender = models.CharField(
        max_length=1,
        choices=GenderChoices.choices,
        null=True,
        blank=True
    )
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)
    history = models.TextField(blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='family_members'
    )
    mother = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children_from_mother'
    )
    father = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children_from_father'
    )
    # Modify spouse field to ManyToManyField
    spouses = models.ManyToManyField(
        'self',
        symmetrical=True,
        blank=True
    )
    chiefdom_of_origin = models.ForeignKey(
        'Chiefdom',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='family_members'
    )
    village_of_origin = models.ForeignKey(
        'Village',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='family_members'
    )
    current_location = models.ForeignKey(
        'Location',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='current_residents'
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class FamilyTree(models.Model):
    """Model representing a family tree."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="family_trees"
    )
    members = models.ManyToManyField(
        FamilyMember, related_name="family_trees", blank=True
    )

    def __str__(self):
        return self.name


class Chiefdom(models.Model):
    """Model representing a Chiefdom."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Village(models.Model):
    """Model representing a Village."""
    name = models.CharField(max_length=100)
    chiefdom = models.ForeignKey(
        Chiefdom,
        on_delete=models.CASCADE,
        related_name='villages'
    )

    class Meta:
        unique_together = ('name', 'chiefdom')

    def __str__(self):
        return f"{self.name}, {self.chiefdom.name}"


class Location(models.Model):
    """Model representing a Location."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Clan(models.Model):
    """Model representing a Clan."""
    surname = models.CharField(max_length=50, unique=True)

    # Additional fields like description can be added if needed.

    def __str__(self):
        return self.surname
