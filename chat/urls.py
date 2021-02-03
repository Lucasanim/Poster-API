from django.urls import path

from chat import views

app_name = 'chat'

urlpatterns = [
    path('socket/<str:room_name>/', views.home, name="chat_home"),
    path('threads/', views.ReturnThreads.as_view(), name='threads'),
]
