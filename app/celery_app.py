from celery import Celery

celery_app = Celery(
    "compliance_rag",
    broker="redis://localhost:6381/0",
    backend="redis://localhost:6381/0"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
)