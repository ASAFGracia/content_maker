from rest_framework import serializers
from .models import Video, VideoEdit, VideoTextTrack, VideoAudioTrack, YouTubeUpload


class VideoEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoEdit
        fields = ['id', 'edit_type', 'config', 'order_index', 'created_at']
        read_only_fields = ['id', 'created_at']


class VideoTextTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoTextTrack
        fields = ['id', 'text', 'start_time', 'end_time', 'position', 'style', 'created_at']
        read_only_fields = ['id', 'created_at']


class VideoAudioTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoAudioTrack
        fields = ['id', 'audio_file_path', 'start_time', 'volume', 'fade_in', 'fade_out', 'created_at']
        read_only_fields = ['id', 'created_at']


class VideoSerializer(serializers.ModelSerializer):
    edits = VideoEditSerializer(many=True, read_only=True)
    text_tracks = VideoTextTrackSerializer(many=True, read_only=True)
    audio_tracks = VideoAudioTrackSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'file_path', 'thumbnail_path', 'duration',
                  'status', 'project', 'creator', 'template', 'edits', 'text_tracks',
                  'audio_tracks', 'created_at', 'updated_at']
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']


class YouTubeUploadSerializer(serializers.ModelSerializer):
    video = VideoSerializer(read_only=True)
    video_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = YouTubeUpload
        fields = ['id', 'video', 'video_id', 'youtube_video_id', 'scheduled_time',
                  'uploaded_at', 'status', 'description', 'tags', 'created_at', 'updated_at']
        read_only_fields = ['id', 'youtube_video_id', 'uploaded_at', 'created_at', 'updated_at']

