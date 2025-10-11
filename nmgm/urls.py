from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("import/", views.import_data, name="import_data"),
    path("clear_threads/", views.clear_threads, name="clear_threads"),
]
