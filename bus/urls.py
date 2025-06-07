from django.urls import path
from . import views


urlpatterns = [
    path("home",views.home,name="home"),
    path("view_schedule/<int:schedule_code>",views.view_schedule,name="view_schedule"),
    path("view_status", views.view_status, name="view_status"),
    path("upload_img", views.upload_img_and_check , name="upload_img")
]