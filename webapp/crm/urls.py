from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ProjectViewSet, TaskViewSet, MeetingViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'meetings', MeetingViewSet, basename='meeting')

urlpatterns = [
    path('', include(router.urls)),
]

