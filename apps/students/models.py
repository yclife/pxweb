from django.db import models
from apps.users.models import User


class Student(models.Model):
    STATUS_CHOICES = (
        ('active', '在读'),
        ('graduated', '已毕业'),
        ('suspended', '休学'),
        ('dropped', '退学'),
    )
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name='用户'
    )
    student_id = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='学号'
    )
    department = models.CharField(max_length=200, blank=True, verbose_name='院系')
    grade = models.CharField(max_length=100, blank=True, verbose_name='年级')
    enrollment_date = models.DateField(verbose_name='入学日期')
    graduation_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='毕业日期'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='状态'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'students_student'
        verbose_name = '学员'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student_id} - {self.user.username}"


class StudentContact(models.Model):
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name='contact_info',
        verbose_name='学员'
    )
    emergency_contact = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name='紧急联系人'
    )
    emergency_phone = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name='紧急联系电话'
    )
    address = models.TextField(blank=True, verbose_name='联系地址')
    parent_name = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name='家长姓名'
    )
    parent_phone = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name='家长电话'
    )
    
    class Meta:
        db_table = 'students_studentcontact'
        verbose_name = '学员联系信息'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.student.user.username} 的联系信息"


class StudentAchievement(models.Model):
    ACHIEVEMENT_TYPES = (
        ('academic', '学术成就'),
        ('sports', '体育成就'),
        ('art', '艺术成就'),
        ('other', '其他成就'),
    )
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name='学员'
    )
    achievement_type = models.CharField(
        max_length=10,
        choices=ACHIEVEMENT_TYPES,
        verbose_name='成就类型'
    )
    title = models.CharField(max_length=200, verbose_name='成就标题')
    description = models.TextField(blank=True, verbose_name='成就描述')
    date_achieved = models.DateField(verbose_name='获得日期')
    certificate_file = models.FileField(
        upload_to='student_achievements/',
        blank=True,
        null=True,
        verbose_name='证书文件'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'students_studentachievement'
        verbose_name = '学员成就'
        verbose_name_plural = verbose_name
        ordering = ['-date_achieved']
    
    def __str__(self):
        return f"{self.student.user.username} - {self.title}"


class StudentPhoto(models.Model):
    """学员相片模型"""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='学员'
    )
    photo = models.ImageField(
        upload_to='student_photos/%Y/%m/%d/',
        verbose_name='相片'
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='相片描述'
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name='是否为主相片'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='上传时间'
    )
    
    class Meta:
        db_table = 'students_studentphoto'
        verbose_name = '学员相片'
        verbose_name_plural = verbose_name
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.student.user.username} 的相片"
    
    def get_photo_url(self):
        """获取相片URL"""
        if self.photo:
            return self.photo.url
        return None
