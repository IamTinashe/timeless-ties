from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model."""

    # Add additional fields if needed, e.g.,
    # middle_name = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.username


class FamilyMember(models.Model):
    """Model representing a family member."""

    first_name = models.CharField(max_length=50, null=True,)
    last_name = models.CharField(max_length=50, null=True,)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="family_members",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
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
