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
    'youtube_upload_scheduler',
    default_args=default_args,
    description='Планирование загрузки видео на YouTube',
    schedule_interval=timedelta(minutes=15),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['youtube', 'upload'],
)

def check_scheduled_uploads():
    """Проверка запланированных загрузок на YouTube"""
    import requests
    import os
    from datetime import datetime
    
    api_url = os.getenv('WEBAPP_URL', 'http://webapp:8000')
    now = datetime.now().isoformat()
    
    response = requests.get(
        f'{api_url}/api/video/youtube/',
        params={'status': 'scheduled', 'scheduled_time__lte': now}
    )
    
    if response.status_code == 200:
        uploads = response.json().get('results', [])
        print(f"Найдено запланированных загрузок: {len(uploads)}")
        
        for upload in uploads:
            upload_id = upload['id']
            trigger_response = requests.post(
                f'{api_url}/api/video/youtube/{upload_id}/schedule/',
                json={'scheduled_time': upload['scheduled_time']},
                headers={'Authorization': f'Bearer {os.getenv("API_TOKEN", "")}'}
            )
            print(f"Запущена загрузка {upload_id}: {trigger_response.status_code}")
    
    return len(uploads) if response.status_code == 200 else 0

upload_task = PythonOperator(
    task_id='check_and_upload',
    python_callable=check_scheduled_uploads,
    dag=dag,
)

