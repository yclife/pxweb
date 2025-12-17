import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pxweb.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# 检查用户是否已存在
if not User.objects.filter(username="testuser").exists():
    user = User.objects.create_user(
        "testuser", 
        "test@example.com", 
        "testpass123", 
        first_name="Test", 
        last_name="User"
    )
    print(f"用户创建成功: {user.username}")
else:
    print("用户已存在")

# 检查管理员用户
if not User.objects.filter(username="admin").exists():
    admin = User.objects.create_superuser(
        "admin",
        "admin@example.com",
        "admin123",
        first_name="Admin",
        last_name="User"
    )
    print(f"管理员创建成功: {admin.username}")
else:
    print("管理员已存在")
