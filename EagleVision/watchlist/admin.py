from django.contrib import admin
from .models import OverallWatchlist, PersonalWatchlist

# Register your models here.

admin.site.register(PersonalWatchlist)
admin.site.register(OverallWatchlist)