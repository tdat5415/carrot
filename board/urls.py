from django.urls import path
from . import views

# 내아이피 110.11.54.124
# center의 urls가 여기로 보냄
app_name = 'board'
urlpatterns = [
    path('board/', views.board, name='board'),
    path('board/<int:board_idx>/', views.detail, name='detail'),
    path('board/create/', views.create, name='create'),
    path('index/', views.index, name='index'),
]