from app.inicio import views
from django.urls import path

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('<int:user_id>/update_perfil_user/', views.update_perfil_user, name='update_perfil_user'),
    path('ver_planes/', views.verPlanes, name='ver_planes'),
    path('<int:id_user>/change_password/', views.changePassword, name='change_password'),
    path("chat_bot/", views.ChatBotView.as_view(), name="chat_bot"),
]