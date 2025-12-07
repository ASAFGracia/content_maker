from rest_framework import serializers
from .models import VideoTemplate


class VideoTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoTemplate
        fields = ['id', 'name', 'description', 'config', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

