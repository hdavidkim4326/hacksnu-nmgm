from django.urls import path
from . import views

urlpatterns = [

    path('',views.landing_view, name='landing'),
    path('prototype/',views.prototype_view, name='prototype'),
    path('report/',views.report_view, name='report'),
]

