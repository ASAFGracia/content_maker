from django.core.management.base import BaseCommand
from templates.models import VideoTemplate


class Command(BaseCommand):
    help = 'Инициализация базовых шаблонов обработки видео'

    def handle(self, *args, **options):
        templates = [
            {
                'name': 'Базовый шаблон',
                'description': 'Простая обработка без изменений',
                'config': {
                    'edits': [],
                    'text_overlay': False,
                    'audio_overlay': False
                }
            },
            {
                'name': 'Шаблон с текстом',
                'description': 'Автоматическое добавление текста внизу экрана',
                'config': {
                    'edits': [],
                    'text_overlay': True,
                    'text_position': 'bottom',
                    'text_style': {
                        'font_size': 50,
                        'color': 'white',
                        'font': 'Arial'
                    }
                }
            },
            {
                'name': 'Шаблон с затемнением',
                'description': 'Добавление затемнения в начале и конце',
                'config': {
                    'edits': [
                        {
                            'type': 'fade',
                            'fade_in': 1.0,
                            'fade_out': 1.0
                        }
                    ],
                    'text_overlay': False
                }
            },
            {
                'name': 'Ручное редактирование',
                'description': 'Полный контроль над редактированием',
                'config': {
                    'edits': [],
                    'manual_mode': True
                }
            }
        ]

        for template_data in templates:
            template, created = VideoTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    'description': template_data['description'],
                    'config': template_data['config']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан шаблон: {template.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Шаблон уже существует: {template.name}'))

