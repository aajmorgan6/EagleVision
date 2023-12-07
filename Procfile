web: cd ./EagleVision && celery -A EagleVision worker && celery -A EagleVision beat && python manage.py migrate && python manage.py makesuper && gunicorn EagleVision.wsgi --bind 0.0.0.0:$PORT
