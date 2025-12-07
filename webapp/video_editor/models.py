from django.db import models
from django.conf import settings
import uuid


class Video(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('processing', 'Обработка'),
        ('ready', 'Готово'),
        ('published', 'Опубликовано'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    thumbnail_path = models.CharField(max_length=500, blank=True)
    duration = models.IntegerField(null=True, blank=True)  # в секундах
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    project = models.ForeignKey('crm.Project', on_delete=models.SET_NULL, null=True, blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    template = models.ForeignKey('templates.VideoTemplate', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'videos'
        ordering = ['-created_at']


class VideoEdit(models.Model):
    EDIT_TYPES = [
        ('cut', 'Обрезка'),
        ('audio_overlay', 'Наложение звука'),
        ('text_overlay', 'Текст на экране'),
        ('image_overlay', 'Вставка изображения'),
        ('fade', 'Затемнение/Потухание'),
        ('volume', 'Регулировка громкости'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='edits')
    edit_type = models.CharField(max_length=50, choices=EDIT_TYPES)
    config = models.JSONField(default=dict)  # параметры редактирования
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'video_edits'
        ordering = ['order_index']


class VideoTextTrack(models.Model):
    POSITION_CHOICES = [
        ('top', 'Верх'),
        ('center', 'Центр'),
        ('bottom', 'Низ'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='text_tracks')
    text = models.TextField()
    start_time = models.DecimalField(max_digits=10, decimal_places=3)
    end_time = models.DecimalField(max_digits=10, decimal_places=3)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES, default='bottom')
    style = models.JSONField(default=dict)  # стили текста (цвет, шрифт, размер)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'video_text_tracks'
        ordering = ['start_time']


class VideoAudioTrack(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='audio_tracks')
    audio_file_path = models.CharField(max_length=500)
    start_time = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    volume = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    fade_in = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fade_out = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'video_audio_tracks'
        ordering = ['start_time']


class YouTubeUpload(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('scheduled', 'Запланировано'),
        ('uploading', 'Загружается'),
        ('uploaded', 'Загружено'),
        ('failed', 'Ошибка'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='youtube_uploads')
    youtube_video_id = models.CharField(max_length=100, blank=True)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    uploaded_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'youtube_uploads'
        ordering = ['-scheduled_time']

