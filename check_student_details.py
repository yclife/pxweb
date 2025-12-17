import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pxweb.settings")
import django
django.setup()

from apps.students.models import Student
from django.contrib.auth import get_user_model
User = get_user_model()

# 检查所有学员
students = Student.objects.all()
print(f"学员总数: {students.count()}")
for student in students:
    print(f"\n学员ID: {student.id}")
    print(f"学号: {student.student_id}")
    print(f"院系: {student.department}")
    print(f"年级: {student.grade}")
    print(f"状态: {student.status}")
    
    # 检查关联的用户
    if student.user:
        user = student.user
        print(f"关联用户ID: {user.id}")
        print(f"用户名: {user.username}")
        print(f"姓名: {user.first_name} {user.last_name}")
        print(f"邮箱: {user.email}")
        print(f"电话: {user.phone}")
        print(f"用户类型: {user.user_type}")
    else:
        print("没有关联用户")
