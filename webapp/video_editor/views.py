from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid
from .models import Video, VideoEdit, VideoTextTrack, VideoAudioTrack, YouTubeUpload
from .serializers import (
    VideoSerializer, VideoEditSerializer, VideoTextTrackSerializer,
    VideoAudioTrackSerializer, YouTubeUploadSerializer
)
from .tasks import process_video, translate_text, generate_tts, upload_to_youtube
from .utils import get_video_duration, generate_thumbnail


class VideoViewSet(viewsets.ModelViewSet):
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        return Video.objects.filter(creator=user)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Загрузка видео файла"""
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        video_file = request.FILES['file']
        title = request.data.get('title', video_file.name)
        
        # Сохранение файла
        file_extension = os.path.splitext(video_file.name)[1]
        file_name = f"{uuid.uuid4()}{file_extension}"
        file_path = default_storage.save(f'uploads/videos/{file_name}', video_file)

        # Создание записи видео
        video = Video.objects.create(
            title=title,
            file_path=file_path,
            creator=request.user,
            status='draft'
        )

        # Получение длительности и создание превью
        try:
            duration = get_video_duration(file_path)
            video.duration = duration
            thumbnail_path = generate_thumbnail(file_path, video.id)
            video.thumbnail_path = thumbnail_path
            video.save()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = self.get_serializer(video)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def apply_template(self, request, pk=None):
        """Применение шаблона к видео"""
        video = self.get_object()
        template_id = request.data.get('template_id')
        
        if not template_id:
            return Response({'error': 'template_id required'}, status=status.HTTP_400_BAD_REQUEST)

        from templates.models import VideoTemplate
        try:
            template = VideoTemplate.objects.get(id=template_id)
            video.template = template
            video.save()
            
            # Запуск обработки видео по шаблону
            process_video.delay(str(video.id), str(template_id))
            
            return Response({'status': 'processing started'})
        except VideoTemplate.DoesNotExist:
            return Response({'error': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def add_text_track(self, request, pk=None):
        """Добавление текстовой дорожки"""
        video = self.get_object()
        serializer = VideoTextTrackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(video=video)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_audio_track(self, request, pk=None):
        """Добавление аудио дорожки"""
        video = self.get_object()
        if 'audio_file' not in request.FILES:
            return Response({'error': 'No audio file provided'}, status=status.HTTP_400_BAD_REQUEST)

        audio_file = request.FILES['audio_file']
        file_extension = os.path.splitext(audio_file.name)[1]
        file_name = f"{uuid.uuid4()}{file_extension}"
        audio_path = default_storage.save(f'uploads/audio/{file_name}', audio_file)

        audio_track = VideoAudioTrack.objects.create(
            video=video,
            audio_file_path=audio_path,
            start_time=request.data.get('start_time', 0),
            volume=request.data.get('volume', 1.0),
            fade_in=request.data.get('fade_in', 0),
            fade_out=request.data.get('fade_out', 0)
        )

        serializer = VideoAudioTrackSerializer(audio_track)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def translate_text(self, request, pk=None):
        """Перевод текста с английского на русский"""
        video = self.get_object()
        text = request.data.get('text', '')
        if not text:
            return Response({'error': 'text required'}, status=status.HTTP_400_BAD_REQUEST)

        translated = translate_text.delay(text)
        return Response({'translated_text': translated.get()})

    @action(detail=True, methods=['post'])
    def generate_tts(self, request, pk=None):
        """Генерация речи из текста"""
        video = self.get_object()
        text = request.data.get('text', '')
        language = request.data.get('language', 'ru')
        
        if not text:
            return Response({'error': 'text required'}, status=status.HTTP_400_BAD_REQUEST)

        audio_path = generate_tts.delay(text, language)
        return Response({'audio_path': audio_path.get()})

    @action(detail=True, methods=['post'])
    def render(self, request, pk=None):
        """Рендеринг финального видео"""
        video = self.get_object()
        video.status = 'processing'
        video.save()
        
        process_video.delay(str(video.id))
        return Response({'status': 'rendering started'})


class VideoEditViewSet(viewsets.ModelViewSet):
    serializer_class = VideoEditSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        video_id = self.request.query_params.get('video_id')
        if video_id:
            return VideoEdit.objects.filter(video_id=video_id)
        return VideoEdit.objects.none()


class YouTubeUploadViewSet(viewsets.ModelViewSet):
    serializer_class = YouTubeUploadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return YouTubeUpload.objects.filter(video__creator=user)

    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """Планирование загрузки на YouTube"""
        upload = self.get_object()
        scheduled_time = request.data.get('scheduled_time')
        
        if not scheduled_time:
            return Response({'error': 'scheduled_time required'}, status=status.HTTP_400_BAD_REQUEST)

        upload.scheduled_time = scheduled_time
        upload.status = 'scheduled'
        upload.save()

        # Генерация описания через ChatGPT
        if not upload.description:
            from .utils import generate_video_description
            description = generate_video_description(upload.video)
            upload.description = description
            upload.save()

        # Планирование загрузки
        upload_to_youtube.apply_async(
            args=[str(upload.id)],
            eta=scheduled_time
        )

        return Response({'status': 'scheduled'})

