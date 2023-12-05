from django.db import models
from django.utils.translation import gettext_lazy as _

class Student(models.Model):
    username = models.CharField(
        _('username'),
        max_length=50, 
        blank=False)
    majors = models.CharField( # will also double as department for admin
        _('majors'),
        max_length=200, blank=False)
    minors = models.CharField(
        _('minors'),
        max_length=200,
        blank=True,
        null=True
    )
    grad_year = models.CharField(
        _('graduation year'),
        max_length=4,
        blank=False,
        null=True
    )
    grad_sem = models.CharField(
        _('graduation semester'),
        max_length=10,
        blank=False,
        null=True
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be '
            'treated as active. Unselect this instead '
            'of deleting accounts.'
        ),
    ) 
    eagle_id = models.CharField(
        _('eagleid'),
        default="",
        blank=False,
        max_length=8,
        unique=True
    )
    is_superuser = models.BooleanField(default = False) 
    is_student = models.BooleanField(default=True)

    # USERNAME_FIELD = "username"

    # @classmethod
    # def create(self, username, majors, minors, grad_year, grad_sem):
    #     return self(username, majors, minors, grad_year, grad_sem)

    def __str__(self):
        return self.username