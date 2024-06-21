from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

handler404 = 'main.views.handler404'

urlpatterns = [
    path('', views.home, name='home'),
    path('chats/', views.chat_list, name='chat_list'),
    path('chats/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('chats/<int:chat_id>/delete/', views.delete_chat, name='delete_chat'),
    path('signup/', views.signup, name='signup'),
    path('start_chat/<int:user_id>/', views.start_chat, name='start_chat'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('create_group/', views.create_group, name='create_group'),
    path('group_chat/<int:group_id>/add_participant/', views.add_participant, name='add_participant'),
    path('group_list/', views.group_list, name='group_list'),
    path('group_chat/<int:group_id>/', views.group_chat_detail, name='group_chat_detail'),
]
