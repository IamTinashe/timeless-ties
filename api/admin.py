from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from api.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin view for CustomUser model."""

    fieldsets = UserAdmin.fieldsets  # Use default fieldsets
    add_fieldsets = UserAdmin.add_fieldsets  # Use default add_fieldsets
