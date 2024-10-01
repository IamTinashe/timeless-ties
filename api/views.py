from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import permissions, viewsets, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import FamilyMember, FamilyTree, Chiefdom, Village, Location, Event
from .serializers import (FamilyMemberSerializer, FamilyTreeSerializer,
                          UserSerializer, ChiefdomSerializer, VillageSerializer, LocationSerializer, EventSerializer)

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing user instances."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class FamilyMemberViewSet(viewsets.ModelViewSet):
    serializer_class = FamilyMemberSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # During schema generation, request may not be authenticated
        if getattr(self, 'swagger_fake_view', False):
            return FamilyMember.objects.all().select_related(
                'mother', 'father', 'chiefdom_of_origin', 'village_of_origin', 'current_location'
            ).prefetch_related('spouses')
        return FamilyMember.objects.filter(user=self.request.user).select_related(
            'mother', 'father', 'chiefdom_of_origin', 'village_of_origin', 'current_location'
        ).prefetch_related('spouses')

    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FamilyTreeViewSet(viewsets.ModelViewSet):
    """ViewSet for CRUD operations on FamilyTree."""

    serializer_class = FamilyTreeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            # Return all FamilyTree instances for schema generation
            return FamilyTree.objects.all().select_related(
                'user',  # Adjust related fields as necessary
                # Add other related fields if applicable
            )
        if self.request.user.is_authenticated:
            # Return FamilyTree instances related to the authenticated user
            return FamilyTree.objects.filter(owner=self.request.user).select_related(
                'user',  # Adjust related fields as necessary
                # Add other related fields if applicable
            )
        # Return an empty queryset for unauthenticated users (shouldn't occur due to IsAuthenticated)
        return FamilyTree.objects.none()

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


class EventViewSet(viewsets.ModelViewSet):
    """ViewSet for CRUD operations on Event."""

    serializer_class = EventSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            # Return all Event instances for schema generation
            return Event.objects.all().select_related('family_member', 'related_fields_here')
        if self.request.user.is_authenticated:
            # Return Event instances related to the authenticated user
            return Event.objects.filter(family_member__user=self.request.user).select_related(
                'family_member', 'related_fields_here'
            )
        # Return an empty queryset for unauthenticated users (shouldn't occur due to IsAuthenticated)
        return Event.objects.none()

    def perform_create(self, serializer):
        serializer.save(family_member=self.request.user.familymember)  # Adjust as per your model relationships


class FamilyTreeAPIView(APIView):
    """API view to retrieve family tree by clan name (last_name)."""
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def get(self, request, clan_name, format=None):
        # Use select_related to fetch related objects in a single query
        family_members = FamilyMember.objects.filter(
            last_name__iexact=clan_name,
            user=request.user
        ).select_related('mother', 'father', 'chiefdom_of_origin', 'village_of_origin',
                         'current_location').prefetch_related('spouses')

        if not family_members.exists():
            return Response({"detail": "Clan not found."}, status=status.HTTP_404_NOT_FOUND)

        roots = family_members.filter(mother__isnull=True, father__isnull=True)

        def build_tree(member, visited=None):
            if visited is None:
                visited = set()
            if member.id in visited:
                return None  # or handle appropriately
            visited.add(member.id)
            serializer = FamilyMemberSerializer(member)
            member_data = serializer.data
            children = family_members.filter(Q(mother=member) | Q(father=member))
            member_data['children'] = [build_tree(child, visited.copy()) for child in children if
                                       child.id not in visited]
            return member_data

        tree = [build_tree(root) for root in roots]

        paginator = PageNumberPagination()
        paginator.page_size = 10  # Adjust as needed
        paginated_tree = paginator.paginate_queryset(tree, request)
        return paginator.get_paginated_response(paginated_tree)
