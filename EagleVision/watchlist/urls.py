from django.urls import path
from . import views

urlpatterns = [
    path("", views.watchlistOverview, name="watchlist"),
    path("<str:class_id>/", views.watchlistStudents, name="studentList")
]