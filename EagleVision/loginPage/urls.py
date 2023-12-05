from django.urls import path
from . import views
# from .forms import CustomAuthForm
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("callback", views.callback, name="callback"),
    path("signUp", views.signUp, name="signUp")
]