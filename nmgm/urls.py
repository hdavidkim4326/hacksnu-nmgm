from django.urls import path
from . import views

urlpatterns = [
<<<<<<< HEAD
    path('', views.home, name='home'),
    path('add_user/', views.add_user, name='add_user'),
]
=======
    path("", views.home, name="home"),
    path("import/", views.import_data, name="import_data"),
    path("clear_threads/", views.clear_threads, name="clear_threads"),
]
>>>>>>> 8136b315 ([add thread cut])
