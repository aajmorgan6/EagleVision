from django.urls import path
from . import views

urlpatterns = [
    path("", views.profile, name="profile"),
    path("editStudentProfile/", views.editStudentProfile, name="editStudentProfile"),
    path("editAdminProfile/", views.editAdminProfile, name="editAdminProfile"),
    path('current_change/', views.current_change),
    path('get_config/', views.get_config),
    path('removeClass/<str:class_id>/', views.removeClass, name="removeClass"),
    path('changeAlert', views.changeAlert, name="changeAlert")
]