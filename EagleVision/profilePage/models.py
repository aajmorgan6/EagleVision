from django.db import models

# Create your models here.
class SystemConfig(models.Model):
    system_open = models.BooleanField(default=True)
    semester_code = models.CharField(max_length=6) # i.e. 2024S
    semester_name = models.CharField(max_length=50) # i.e. Spring Add/Drop 2024
    
    @staticmethod
    def is_system_open():
        config = SystemConfig.objects.first()
        return config.system_open if config else True

    