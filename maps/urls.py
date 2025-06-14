from django.urls import path
from . import views

urlpatterns = [
    path("api/locations/", views.campus_locations_json, name="campus_locations_json"),
    path("display_map",views.display_map,name="display_map"),
    path("display_map_menu",views.display_map_menu,name="display_map_menu"),

    path("add_location",views.add_location,name="add_location"),
    path("remove_location",views.remove_location,name="remove_location"),
    path("view_all",views.view_all,name="view_all"),
    path("update_location/<int:id>",views.update_location,name="update_location")
]