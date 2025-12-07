from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VideoViewSet, VideoEditViewSet, YouTubeUploadViewSet

router = DefaultRouter()
router.register(r'videos', VideoViewSet, basename='video')
router.register(r'edits', VideoEditViewSet, basename='edit')
router.register(r'youtube', YouTubeUploadViewSet, basename='youtube')

urlpatterns = [
    path('', include(router.urls)),
]

