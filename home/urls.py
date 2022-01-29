from django.urls import path
from . import views

# center의 urls가 여기로 보냄
app_name = 'home'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('join/', views.join, name='join'),
    path('join/check/', views.join_check, name='join_check'),
    path('location/', views.location, name='location'),
]