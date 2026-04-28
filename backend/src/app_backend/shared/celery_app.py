"""
Celery Configuration untuk Background Tasks.
Mendefinisikan task queue dengan Redis sebagai message broker.
"""

from celery import Celery
from celery.signals import worker_init, worker_shutdown

# Celery app instance
celery_app = Celery(
    "app_backend",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
    include=[
        "app_backend.shared.tasks.ai_tasks",
        "app_backend.shared.tasks.vacancy_tasks",
        "app_backend.shared.tasks.notification_tasks",
        "app_backend.shared.tasks.report_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Task routing
    task_routes={
        "app_backend.shared.tasks.ai_tasks.*": {"queue": "ai"},
        "app_backend.shared.tasks.vacancy_tasks.*": {"queue": "vacancy"},
        "app_backend.shared.tasks.notification_tasks.*": {"queue": "notification"},
        "app_backend.shared.tasks.report_tasks.*": {"queue": "report"},
    },
)


@worker_init.connect
def init_worker(*args, **kwargs):
    """Initialize worker connections."""
    pass


@worker_shutdown.connect
def shutdown_worker(*args, **kwargs):
    """Cleanup worker connections."""
    pass
