from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Custom permission to only allow owners to edit objects."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow owners to edit; read-only for others."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
