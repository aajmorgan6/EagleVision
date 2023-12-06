web: cd ./EagleVision && celery -A EagleVision worker -l info && python manage.py migrate && gunicorn EagleVision.wsgi --bind 0.0.0.0:$PORT
