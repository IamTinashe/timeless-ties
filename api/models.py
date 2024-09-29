from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # Additional fields if needed
    pass

class FamilyMember(models.Model):
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    # Relationships
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

