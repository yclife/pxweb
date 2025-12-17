import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pxweb.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# 检查所有用户
users = User.objects.all()
print(f"总用户数: {users.count()}")
for user in users:
    print(f"ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}, 激活: {user.is_active}, 最后登录: {user.last_login}")
    
# 检查testuser
try:
    testuser = User.objects.get(username="testuser")
    print(f"\ntestuser详情:")
    print(f"  用户名: {testuser.username}")
    print(f"  邮箱: {testuser.email}")
    print(f"  激活: {testuser.is_active}")
    print(f"  密码设置: {testuser.has_usable_password()}")
    print(f"  检查密码 'testpass123': {testuser.check_password('testpass123')}")
except User.DoesNotExist:
    print("\ntestuser不存在")
