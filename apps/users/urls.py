from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # 认证相关
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    
    # 用户管理
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/me/', views.CurrentUserView.as_view(), name='current-user'),
    path('users/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # 健康检查
    path('health/', views.health_check, name='health-check'),
]
