from django.contrib import admin
from .models import Video, VideoEdit, VideoTextTrack, VideoAudioTrack, YouTubeUpload


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'status', 'duration', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']


@admin.register(VideoEdit)
class VideoEditAdmin(admin.ModelAdmin):
    list_display = ['video', 'edit_type', 'order_index']
    list_filter = ['edit_type']


@admin.register(YouTubeUpload)
class YouTubeUploadAdmin(admin.ModelAdmin):
    list_display = ['video', 'status', 'scheduled_time', 'uploaded_at']
    list_filter = ['status', 'scheduled_time']

