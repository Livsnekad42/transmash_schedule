# gunicorn -c gunicorn.py main.wsgi&
gunicorn -c ../gunicorn.py main.wsgi&
gunicorn -c gunicorn.py main.asgi:application -k uvicorn.workers.UvicornWorker&

celery --app main worker -Q default --concurrency=1&
celery --app main worker -Q notify_worker --concurrency=2&