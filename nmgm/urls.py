from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('user_detail',views.user_detail, name='user_detail'),
    path('landing',views.landing, name='landing'),
]