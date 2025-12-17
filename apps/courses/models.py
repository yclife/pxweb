from django.db import models
from apps.users.models import User


class Course(models.Model):
    DIFFICULTY_LEVELS = (
        ('beginner', '初级'),
        ('intermediate', '中级'),
        ('advanced', '高级'),
    )
    
    course_code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='课程代码'
    )
    course_name = models.CharField(max_length=200, verbose_name='课程名称')
    description = models.TextField(blank=True, verbose_name='课程描述')
    category = models.CharField(max_length=100, blank=True, verbose_name='课程类别')
    total_hours = models.IntegerField(verbose_name='总学时')
    credit = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name='学分'
    )
    difficulty_level = models.CharField(
        max_length=15,
        choices=DIFFICULTY_LEVELS,
        default='beginner',
        verbose_name='难度级别'
    )
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'courses_course'
        verbose_name = '课程'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


class CourseSchedule(models.Model):
    STATUS_CHOICES = (
        ('scheduled', '已安排'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )
    
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='schedules',
        verbose_name='课程'
    )
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.CASCADE,
        related_name='course_schedules',
        verbose_name='教师'
    )
    schedule_date = models.DateField(verbose_name='上课日期')
    start_time = models.TimeField(verbose_name='开始时间')
    end_time = models.TimeField(verbose_name='结束时间')
    classroom = models.CharField(max_length=100, blank=True, verbose_name='教室')
    max_students = models.IntegerField(default=30, verbose_name='最大学生数')
    current_students = models.IntegerField(default=0, verbose_name='当前学生数')
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name='状态'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'courses_courseschedule'
        verbose_name = '课程安排'
        verbose_name_plural = verbose_name
        ordering = ['schedule_date', 'start_time']
    
    def __str__(self):
        return f"{self.course.course_name} - {self.schedule_date} {self.start_time}"


class CourseMaterial(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='materials',
        verbose_name='课程'
    )
    title = models.CharField(max_length=200, verbose_name='资料标题')
    description = models.TextField(blank=True, verbose_name='资料描述')
    file = models.FileField(
        upload_to='course_materials/',
        verbose_name='资料文件'
    )
    file_size = models.IntegerField(blank=True, null=True, verbose_name='文件大小')
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='上传者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    
    class Meta:
        db_table = 'courses_coursematerial'
        verbose_name = '课程资料'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.course.course_name} - {self.title}"
