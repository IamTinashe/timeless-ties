from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets

from .models import FamilyMember, FamilyTree
from .serializers import (FamilyMemberSerializer, FamilyTreeSerializer,
                          UserSerializer)

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing user instances."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class FamilyMemberViewSet(viewsets.ModelViewSet):
    """ViewSet for CRUD operations on FamilyMember."""

    queryset = FamilyMember.objects.all()
    serializer_class = FamilyMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FamilyMember.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FamilyTreeViewSet(viewsets.ModelViewSet):
    """ViewSet for CRUD operations on FamilyTree."""

    queryset = FamilyTree.objects.all()
    serializer_class = FamilyTreeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FamilyTree.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
