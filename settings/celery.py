
CELERY_RESULT_BACKEND = "mongodb"

CELERY_MONGODB_BACKEND_SETTINGS = {
    "host": "127.0.0.1",
    "port": 27017,
    "database": "celery",
    "taskmeta_collection": "taskmeta",
}

TASKS_ENABLED = dict(
    AVATAR_RESIZE = 1,
    MESSAGE_STORE_READED = 1,
    MESSAGE_DELETE = 1,
)

TASKS_ENABLED = {}

