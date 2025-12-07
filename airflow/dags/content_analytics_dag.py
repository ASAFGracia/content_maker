from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'content_maker',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'content_analytics',
    default_args=default_args,
    description='Сбор аналитики по контенту',
    schedule_interval=timedelta(hours=6),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['analytics', 'reporting'],
)

def collect_analytics():
    """Сбор аналитики по видео и проектам"""
    import requests
    import os
    
    api_url = os.getenv('WEBAPP_URL', 'http://webapp:8000')
    
    # Сбор статистики по видео
    videos_response = requests.get(f'{api_url}/api/video/videos/')
    if videos_response.status_code == 200:
        videos = videos_response.json().get('results', [])
        total_videos = len(videos)
        published_videos = len([v for v in videos if v['status'] == 'published'])
        
        print(f"Всего видео: {total_videos}")
        print(f"Опубликовано: {published_videos}")
    
    # Сбор статистики по задачам
    tasks_response = requests.get(f'{api_url}/api/crm/tasks/')
    if tasks_response.status_code == 200:
        tasks = tasks_response.json().get('results', [])
        completed_tasks = len([t for t in tasks if t['status'] == 'done'])
        
        print(f"Всего задач: {len(tasks)}")
        print(f"Выполнено: {completed_tasks}")

analytics_task = PythonOperator(
    task_id='collect_analytics',
    python_callable=collect_analytics,
    dag=dag,
)

