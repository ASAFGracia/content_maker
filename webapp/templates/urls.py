from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoTemplateViewSet

router = DefaultRouter()
router.register(r'', VideoTemplateViewSet, basename='template')

urlpatterns = [
    path('', include(router.urls)),
]

