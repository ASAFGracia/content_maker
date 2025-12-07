from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import VideoTemplate
from .serializers import VideoTemplateSerializer


class VideoTemplateViewSet(viewsets.ModelViewSet):
    queryset = VideoTemplate.objects.filter(is_active=True)
    serializer_class = VideoTemplateSerializer
    permission_classes = [IsAuthenticated]

