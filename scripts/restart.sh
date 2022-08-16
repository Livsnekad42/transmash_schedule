pkill -f gunicorn
pkill -f celery
pkill -9 celery
git add db.sqlite3
git commit -m "fix: DB"
git checkout .
git pull
source ./venv/bin/activate
gunicorn -c gunicorn.py main.asgi:application -k uvicorn.workers.UvicornWorker&
celery --app main worker -Q default --concurrency=1&
celery --app main worker -Q notify_worker --concurrency=1&