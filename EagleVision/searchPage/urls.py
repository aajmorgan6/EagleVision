from django.urls import path
from . import views

urlpatterns = [
    path("", views.landingPage, name="search"),
    path("add", views.notification_selection, name="add"),
]