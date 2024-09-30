from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets, filters, serializers

from .models import FamilyMember, FamilyTree, Chiefdom, Village, Location
from .serializers import (FamilyMemberSerializer, FamilyTreeSerializer,
                          UserSerializer, ChiefdomSerializer, VillageSerializer, LocationSerializer)

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


class ChiefdomViewSet(viewsets.ModelViewSet):
    queryset = Chiefdom.objects.all()
    serializer_class = ChiefdomSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class VillageViewSet(viewsets.ModelViewSet):
    queryset = Village.objects.all()
    serializer_class = VillageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'chiefdom__name']


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

