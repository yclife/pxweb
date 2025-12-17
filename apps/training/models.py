from django.db import models
from apps.users.models import User
from apps.courses.models import CourseSchedule
from apps.students.models import Student


class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('enrolled', '已选课'),
        ('completed', '已完成'),
        ('dropped', '已退课'),
    )
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='学员'
    )
    course_schedule = models.ForeignKey(
        CourseSchedule,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='课程安排'
    )
    enrollment_date = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='选课时间'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='enrolled',
        verbose_name='状态'
    )
    final_grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='最终成绩'
    )
    completion_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='完成时间'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'training_enrollment'
        verbose_name = '选课记录'
        verbose_name_plural = verbose_name
        unique_together = ['student', 'course_schedule']
        ordering = ['-enrollment_date']
    
    def __str__(self):
        return f"{self.student.user.username} - {self.course_schedule.course.course_name}"


class StudyHour(models.Model):
    ATTENDANCE_STATUS_CHOICES = (
        ('present', '出席'),
        ('absent', '缺席'),
        ('late', '迟到'),
        ('excused', '请假'),
    )
    
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='study_hours',
        verbose_name='选课记录'
    )
    study_date = models.DateField(verbose_name='学习日期')
    hours_completed = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name='完成学时'
    )
    attendance_status = models.CharField(
        max_length=10,
        choices=ATTENDANCE_STATUS_CHOICES,
        default='present',
        verbose_name='出勤状态'
    )
    notes = models.TextField(blank=True, verbose_name='备注')
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='记录人'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'training_studyhour'
        verbose_name = '学时记录'
        verbose_name_plural = verbose_name
        ordering = ['-study_date']
    
    def __str__(self):
        return f"{self.enrollment.student.user.username} - {self.study_date} - {self.hours_completed}小时"


class Grade(models.Model):
    GRADE_TYPE_CHOICES = (
        ('homework', '作业'),
        ('quiz', '测验'),
        ('exam', '考试'),
        ('final', '期末'),
    )
    
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name='选课记录'
    )
    grade_type = models.CharField(
        max_length=10,
        choices=GRADE_TYPE_CHOICES,
        verbose_name='成绩类型'
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='得分'
    )
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='满分'
    )
    weight = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=1.00,
        verbose_name='权重'
    )
    graded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='评分人'
    )
    graded_at = models.DateTimeField(auto_now_add=True, verbose_name='评分时间')
    notes = models.TextField(blank=True, verbose_name='备注')
    
    class Meta:
        db_table = 'training_grade'
        verbose_name = '成绩记录'
        verbose_name_plural = verbose_name
        ordering = ['-graded_at']
    
    def __str__(self):
        return f"{self.enrollment.student.user.username} - {self.get_grade_type_display()} - {self.score}/{self.max_score}"


class TrainingProgress(models.Model):
    enrollment = models.OneToOneField(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name='选课记录'
    )
    total_hours_required = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name='总需学时'
    )
    hours_completed = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name='已完成学时'
    )
    completion_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='完成百分比'
    )
    last_study_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='最后学习日期'
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'training_trainingprogress'
        verbose_name = '培训进度'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.enrollment.student.user.username} - {self.completion_percentage}%"
    
    def save(self, *args, **kwargs):
        if self.total_hours_required > 0:
            self.completion_percentage = (self.hours_completed / self.total_hours_required) * 100
        super().save(*args, **kwargs)
