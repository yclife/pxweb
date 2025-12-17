import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pxweb.settings")
import django
django.setup()

from apps.students.models import Student
print('学生总数:', Student.objects.count())
for s in Student.objects.all():
    print(f'ID: {s.id}, 学号: {s.student_id}, 用户: {s.user.username if s.user else "None"}')
