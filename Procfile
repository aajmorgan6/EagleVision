web: java -jar waitlist-app-0.6.2.jar && cd ./EagleVision && celery -A EagleVision worker -l info && python manage.py migrate && gunicorn EagleVision.wsgi --bind 0.0.0.0:$PORT
