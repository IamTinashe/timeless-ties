from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
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


class FamilyMemberResource(resources.ModelResource):
    class Meta:
        model = FamilyMember
        fields = (
            'id', 'first_name', 'last_name', 'gender', 'date_of_birth', 'date_of_death', 'history', 'user', 'mother',
            'father', 'spouses', 'chiefdom_of_origin', 'village_of_origin', 'current_location')


@admin.register(FamilyMember)
class FamilyMemberAdmin(ImportExportModelAdmin):
    """
    Admin interface for the FamilyMember model with import/export capabilities.
    """
    resource_class = FamilyMemberResource
    list_display = (
        'first_name',
        'last_name',
        'gender',
        'chiefdom_of_origin',
        'village_of_origin',
        'mother',
        'father',
        'user'
    )
    search_fields = ('first_name', 'last_name')
    list_filter = (
        'gender',
        'chiefdom_of_origin',
        'village_of_origin',
        'user'
    )
    filter_horizontal = ('spouses',)  # Enables a horizontal filter widget for many-to-many fields


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
