import os
from moviepy.editor import VideoFileClip
from PIL import Image
from django.conf import settings
from django.core.files.storage import default_storage
import subprocess


def get_video_duration(file_path):
    """Получение длительности видео в секундах"""
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    if not os.path.exists(full_path):
        return None
    
    try:
        clip = VideoFileClip(full_path)
        duration = int(clip.duration)
        clip.close()
        return duration
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return None


def generate_thumbnail(video_path, video_id):
    """Генерация превью для видео"""
    full_path = os.path.join(settings.MEDIA_ROOT, video_path)
    if not os.path.exists(full_path):
        return None

    try:
        clip = VideoFileClip(full_path)
        frame = clip.get_frame(1)  # Получаем кадр на 1 секунде
        
        # Сохранение превью
        thumbnail_path = f'thumbnails/{video_id}.jpg'
        full_thumbnail_path = os.path.join(settings.MEDIA_ROOT, thumbnail_path)
        os.makedirs(os.path.dirname(full_thumbnail_path), exist_ok=True)
        
        Image.fromarray(frame).save(full_thumbnail_path)
        clip.close()
        
        return thumbnail_path
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return None


def generate_video_description(video):
    """Генерация описания для видео через ChatGPT"""
    from .tasks import generate_description_ai
    
    if not video.description:
        return "Описание будет сгенерировано автоматически"
    
    # Используем существующее описание как основу
    summary = video.description[:500]  # Первые 500 символов
    
    try:
        description = generate_description_ai.delay(summary)
        return description.get(timeout=30)
    except Exception as e:
        print(f"Error generating description: {e}")
        return video.description

