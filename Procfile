web: cd ./EagleVision && python manage.py migrate && python manage.py makesuper && gunicorn EagleVision.wsgi && celery -A EagleVision worker && celery -A EagleVision beat && --bind 0.0.0.0:$PORT
