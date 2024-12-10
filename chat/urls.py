from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('new/', views.new_chat, name='new_chat'),
    path('chat/<int:pk>/', views.chat_detail, name='chat_detail'),
    path('chat/<int:pk>/delete/', views.delete_chat, name='delete_chat'),
    
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
]