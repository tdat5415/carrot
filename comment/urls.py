from django.urls import path
from . import views

# 내아이피 110.11.54.124
# center의 urls가 여기로 보냄
app_name = 'comment'
urlpatterns = [
    path('comment/create/', views.create, name='create'),
    path('comment/<int:comment_idx>/edit/', views.edit, name='edit'),
    path('comment/<int:comment_idx>/delete/', views.delete, name='delete'),
]