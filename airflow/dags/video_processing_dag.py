from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'content_maker',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'video_processing_pipeline',
    default_args=default_args,
    description='Пайплайн обработки видео',
    schedule_interval=timedelta(hours=1),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['video', 'processing'],
)

def check_pending_videos():
    """Проверка видео, ожидающих обработки"""
    import requests
    import os
    
    api_url = os.getenv('WEBAPP_URL', 'http://webapp:8000')
    response = requests.get(f'{api_url}/api/video/videos/?status=processing')
    
    if response.status_code == 200:
        videos = response.json().get('results', [])
        print(f"Найдено видео для обработки: {len(videos)}")
        return len(videos)
    return 0

def process_videos():
    """Обработка видео через API"""
    import requests
    import os
    
    api_url = os.getenv('WEBAPP_URL', 'http://webapp:8000')
    response = requests.get(f'{api_url}/api/video/videos/?status=processing')
    
    if response.status_code == 200:
        videos = response.json().get('results', [])
        for video in videos:
            video_id = video['id']
            process_response = requests.post(
                f'{api_url}/api/video/videos/{video_id}/render/',
                headers={'Authorization': f'Bearer {os.getenv("API_TOKEN", "")}'}
            )
            print(f"Запущена обработка видео {video_id}: {process_response.status_code}")

check_task = PythonOperator(
    task_id='check_pending_videos',
    python_callable=check_pending_videos,
    dag=dag,
)

process_task = PythonOperator(
    task_id='process_videos',
    python_callable=process_videos,
    dag=dag,
)

check_task >> process_task

