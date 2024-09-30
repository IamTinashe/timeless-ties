from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FamilyMemberViewSet, FamilyTreeViewSet, UserViewSet, ChiefdomViewSet, VillageViewSet, \
    LocationViewSet, FamilyTreeAPIView

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"family-members", FamilyMemberViewSet, basename="familymember")
router.register(r"family-trees", FamilyTreeViewSet, basename="familytree")
router.register(r'chiefdoms', ChiefdomViewSet, basename='chiefdom')
router.register(r'villages', VillageViewSet, basename='village')
router.register(r'locations', LocationViewSet, basename='location')

urlpatterns = [
    path("", include(router.urls)),
    path('clans/<str:clan_name>/tree/', FamilyTreeAPIView.as_view(), name='familytree-detail'),
]
