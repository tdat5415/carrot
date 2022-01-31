from django.urls import path
from . import views

# 내아이피 110.11.54.124
# center의 urls가 여기로 보냄
app_name = 'home'
urlpatterns = [
    path('', views.index, name='index'),
    path('auto_login/', views.auto_login, name='auto_login'),
    path('login/', views.login, name='login'),
    path('join/', views.join, name='join'),
    path('join/check/', views.join_check, name='join_check'),
    path('location/', views.location, name='location'),
    path('token/', views.token, name='token'),
]