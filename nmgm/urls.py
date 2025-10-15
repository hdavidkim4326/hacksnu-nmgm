from django.urls import path
from . import views

urlpatterns = [
<<<<<<< HEAD
    path("", views.home, name="home"),
    path("import/", views.import_data, name="import_data"),
    # path("clear_threads/", views.clear_threads, name="clear_threads"),
    # path("clear_emotions/", views.clear_emotions, name="clear_emotions"),
    path("user_report/", views.generate_user_report, name="user_report"),
    path("chatroom_report/", views.generate_chatroom_report, name="chatroom_report"),
    path("edit_message/", views.suggest_message_edit, name="edit_message")
]
=======

    path('',views.landing_view, name='landing'),
    path('prototype/',views.prototype_view, name='prototype'),
    path('report/',views.report_view, name='report'),
]

>>>>>>> 3dd8b20559b1cf4fb28fc32a7b00c1f326172efe
