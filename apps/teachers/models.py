from django.db import models
from apps.users.models import User


class Teacher(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        verbose_name='用户'
    )
    teacher_id = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='教师编号'
    )
    title = models.CharField(max_length=100, blank=True, verbose_name='职称')
    department = models.CharField(max_length=200, blank=True, verbose_name='部门')
    expertise = models.TextField(blank=True, verbose_name='专业领域')
    introduction = models.TextField(blank=True, verbose_name='个人介绍')
    years_of_experience = models.IntegerField(
        default=0, 
        verbose_name='教学年限'
    )
    is_active = models.BooleanField(default=True, verbose_name='是否在职')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'teachers_teacher'
        verbose_name = '教师'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.teacher_id} - {self.user.username}"


class TeacherAvailability(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='availabilities',
        verbose_name='教师'
    )
    day_of_week = models.IntegerField(
        choices=[
            (0, '周一'),
            (1, '周二'),
            (2, '周三'),
            (3, '周四'),
            (4, '周五'),
            (5, '周六'),
            (6, '周日'),
        ],
        verbose_name='星期几'
    )
    start_time = models.TimeField(verbose_name='开始时间')
    end_time = models.TimeField(verbose_name='结束时间')
    is_available = models.BooleanField(default=True, verbose_name='是否可用')
    
    class Meta:
        db_table = 'teachers_teacheravailability'
        verbose_name = '教师可用时间'
        verbose_name_plural = verbose_name
        unique_together = ['teacher', 'day_of_week']
    
    def __str__(self):
        return f"{self.teacher.user.username} - {self.get_day_of_week_display()}"


class TeacherRating(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='教师'
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        verbose_name='学生'
    )
    rating = models.IntegerField(
        choices=[
            (1, '1星'),
            (2, '2星'),
            (3, '3星'),
            (4, '4星'),
            (5, '5星'),
        ],
        verbose_name='评分'
    )
    comment = models.TextField(blank=True, verbose_name='评价内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评价时间')
    
    class Meta:
        db_table = 'teachers_teacherrating'
        verbose_name = '教师评价'
        verbose_name_plural = verbose_name
        unique_together = ['teacher', 'student']
    
    def __str__(self):
        return f"{self.teacher.user.username} - {self.rating}星"
