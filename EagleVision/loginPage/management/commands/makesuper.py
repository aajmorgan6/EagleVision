from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Set up super user for deployment"

    def handle(self, *args, **options):
        try:
            User = get_user_model()
            User.objects.create_superuser('test', 'admin@myproject.com', 'password')
        except:
            raise CommandError("Could not create super user")