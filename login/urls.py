from django.urls import path
from . import views

app_name = 'account'
urlpatterns = [
    path("",views.login,name="login"),
    path("register",views.register,name="register"),
    path("admin",views.admin,name="admin")
]