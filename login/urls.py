from django.urls import path
from . import views
from .views import logout_view

app_name = 'account'
urlpatterns = [

    path("", views.landing, name="landing"),
    path("login/",views.login,name="login"),
    path("register",views.register,name="register"),
    path("admin",views.admin,name="admin"),
    path('logout/', logout_view, name='logout'),
    path("home/", views.home, name="home"),
    path("contact/", views.contact, name="contact"),
    path("about/", views.about, name="about"),
    path("about/", views.about, name="about"),
    path("landing_about/", views.landing_about, name="landing_about"),
    path("landing_contact/", views.landing_contact, name="landing_contact"),
    path("update_profile/",views.update_profile,name="update_profile"),
    path('reset-password/', views.reset_password, name='reset_password'),

]

