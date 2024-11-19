from django.urls import path
from . import views

urlpatterns = [
    path("", views.client_chat, name="client_chat"), 
    path('adminchat/', views.admin_chat, name='admin_chat'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('api/get_chat_messages/', views.get_chat_messages, name='get_chat_messages'),
 ]