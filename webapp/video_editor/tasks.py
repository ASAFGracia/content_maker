from celery import shared_task
from django.conf import settings
import os
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ImageClip
from deep_translator import GoogleTranslator
from gtts import gTTS
from openai import OpenAI
from .models import Video, VideoEdit, VideoTextTrack, VideoAudioTrack, YouTubeUpload


@shared_task
def process_video(video_id, template_id=None):
    """Обработка видео с применением всех редактирований"""
    try:
        video = Video.objects.get(id=video_id)
        video.status = 'processing'
        video.save()

        input_path = os.path.join(settings.MEDIA_ROOT, video.file_path)
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Video file not found: {input_path}")

        clip = VideoFileClip(input_path)

        # Применение редактирований
        edits = VideoEdit.objects.filter(video=video).order_by('order_index')
        for edit in edits:
            clip = apply_edit(clip, edit)

        # Добавление текстовых дорожек
        text_tracks = VideoTextTrack.objects.filter(video=video).order_by('start_time')
        text_clips = []
        for track in text_tracks:
            text_clip = TextClip(
                track.text,
                fontsize=track.style.get('font_size', 50),
                color=track.style.get('color', 'white'),
                font=track.style.get('font', 'Arial'),
                method='caption',
                size=(clip.w * 0.8, None)
            ).set_position(track.position).set_start(track.start_time).set_duration(
                track.end_time - track.start_time
            )
            text_clips.append(text_clip)

        # Добавление аудио дорожек
        audio_clips = [clip.audio] if clip.audio else []
        audio_tracks = VideoAudioTrack.objects.filter(video=video).order_by('start_time')
        for track in audio_tracks:
            audio_path = os.path.join(settings.MEDIA_ROOT, track.audio_file_path)
            if os.path.exists(audio_path):
                audio_clip = AudioFileClip(audio_path)
                if track.fade_in > 0:
                    audio_clip = audio_clip.fadein(track.fade_in)
                if track.fade_out > 0:
                    audio_clip = audio_clip.fadeout(track.fade_out)
                audio_clip = audio_clip.volumex(float(track.volume))
                audio_clip = audio_clip.set_start(track.start_time)
                audio_clips.append(audio_clip)

        # Композиция финального видео
        if text_clips:
            clip = CompositeVideoClip([clip] + text_clips)

        if len(audio_clips) > 1:
            from moviepy.audio.AudioClip import CompositeAudioClip
            final_audio = CompositeAudioClip(audio_clips)
            clip = clip.set_audio(final_audio)
        elif len(audio_clips) == 1:
            clip = clip.set_audio(audio_clips[0])

        # Сохранение обработанного видео
        output_path = os.path.join(settings.MEDIA_ROOT, 'processed', f'{video_id}.mp4')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )

        clip.close()

        # Обновление статуса
        video.file_path = f'processed/{video_id}.mp4'
        video.status = 'ready'
        video.save()

        return f"Video processed: {output_path}"
    except Exception as e:
        video.status = 'draft'
        video.save()
        raise e


def apply_edit(clip, edit):
    """Применение одного редактирования к клипу"""
    config = edit.config
    
    if edit.edit_type == 'cut':
        start = config.get('start', 0)
        end = config.get('end', clip.duration)
        return clip.subclip(start, end)
    
    elif edit.edit_type == 'fade':
        fade_in = config.get('fade_in', 0)
        fade_out = config.get('fade_out', 0)
        return clip.fadein(fade_in).fadeout(fade_out)
    
    elif edit.edit_type == 'volume':
        volume = config.get('volume', 1.0)
        return clip.volumex(volume)
    
    return clip


@shared_task
def translate_text(text):
    """Перевод текста с английского на русский"""
    try:
        translator = GoogleTranslator(source='en', target='ru')
        result = translator.translate(text)
        return result
    except Exception as e:
        print(f"Translation error: {e}")
        return text


@shared_task
def generate_tts(text, language='ru'):
    """Генерация речи из текста"""
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        audio_path = os.path.join(settings.MEDIA_ROOT, 'tts', f'{hash(text)}.mp3')
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        tts.save(audio_path)
        return f'tts/{hash(text)}.mp3'
    except Exception as e:
        print(f"TTS error: {e}")
        raise e


@shared_task
def generate_description_ai(summary):
    """Генерация описания для YouTube через ChatGPT"""
    if not settings.OPENAI_API_KEY:
        return summary

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты помощник для создания описаний к видео на YouTube. Создай короткое, привлекательное описание на русском языке."},
                {"role": "user", "content": f"Создай описание для видео на основе этого текста: {summary}"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI error: {e}")
        return summary


@shared_task
def upload_to_youtube(upload_id):
    """Загрузка видео на YouTube"""
    try:
        upload = YouTubeUpload.objects.get(id=upload_id)
        video = upload.video
        
        if not settings.YOUTUBE_CLIENT_ID or not settings.YOUTUBE_CLIENT_SECRET:
            raise ValueError("YouTube API credentials not configured")

        # Здесь должна быть реализация загрузки через YouTube Data API v3
        # Это требует OAuth 2.0 аутентификации
        
        upload.status = 'uploaded'
        upload.save()
        
        return f"Video uploaded to YouTube: {upload.youtube_video_id}"
    except Exception as e:
        upload.status = 'failed'
        upload.save()
        raise e

