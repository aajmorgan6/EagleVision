web: cd ./waitlistapp && java -jar waitlist-app-0.6.2.jar && cd ../ && cd ./EagleVision && celery -A EagleVision worker -l info && celery -A EagleVision beat -l info && python manage.py migrate && gunicorn EagleVision.wsgi --bind 0.0.0.0:$PORT
