from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FamilyMemberViewSet

router = DefaultRouter()
router.register(r'family-members', FamilyMemberViewSet, basename='family-member')

urlpatterns = [
    path('', include(router.urls)),
]
