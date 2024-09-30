from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FamilyMemberViewSet, FamilyTreeViewSet, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"family-members", FamilyMemberViewSet, basename="familymember")
router.register(r"family-trees", FamilyTreeViewSet, basename="familytree")

urlpatterns = [
    path("", include(router.urls)),
]
