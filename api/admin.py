from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import (
    CustomUser,
    FamilyMember,
    Chiefdom,
    Village,
    Location
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin view for CustomUser model."""

    fieldsets = UserAdmin.fieldsets  # Use default fieldsets
    add_fieldsets = UserAdmin.add_fieldsets  # Use default add_fieldsets


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'gender', 'mother', 'father', 'user')
    search_fields = ('first_name', 'last_name')
    list_filter = ('gender', 'user')
    filter_horizontal = ('spouses',)  # Add this line


@admin.register(Chiefdom)
class ChiefdomAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ('name', 'chiefdom')
    search_fields = ('name',)
    list_filter = ('chiefdom',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
