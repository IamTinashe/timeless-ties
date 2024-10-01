from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FamilyMemberViewSet,
    FamilyTreeViewSet,
    UserViewSet,
    ChiefdomViewSet,
    VillageViewSet,
    LocationViewSet,
    FamilyTreeAPIView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

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
    # JWT token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # To obtain tokens
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # To refresh tokens
]
