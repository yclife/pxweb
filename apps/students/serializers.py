from rest_framework import serializers
from .models import Student, StudentContact, StudentAchievement, StudentPhoto


class StudentContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentContact
        fields = [
            'emergency_contact', 'emergency_phone', 'address',
            'parent_name', 'parent_phone'
        ]


class StudentAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAchievement
        fields = [
            'id', 'achievement_type', 'title', 'description',
            'date_achieved', 'certificate_file', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class StudentPhotoSerializer(serializers.ModelSerializer):
    """学员相片序列化器"""
    photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentPhoto
        fields = ['id', 'student', 'photo', 'photo_url', 'description', 'is_primary', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']
    
    def get_photo_url(self, obj):
        """获取相片URL"""
        request = self.context.get('request')
        if obj.photo and hasattr(obj.photo, 'url'):
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None


class StudentPhotoCreateSerializer(serializers.ModelSerializer):
    """学员相片创建序列化器"""
    class Meta:
        model = StudentPhoto
        fields = ['student', 'photo', 'description', 'is_primary']
    
    def validate(self, data):
        """验证数据"""
        # 如果设置为primary，取消其他相片的primary状态
        if data.get('is_primary', False):
            StudentPhoto.objects.filter(
                student=data['student'], 
                is_primary=True
            ).update(is_primary=False)
        return data


class StudentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    contact_info = StudentContactSerializer(read_only=True)
    achievements = StudentAchievementSerializer(many=True, read_only=True)
    photos = StudentPhotoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'user', 'student_id', 'department', 'grade',
            'enrollment_date', 'graduation_date', 'status',
            'created_at', 'contact_info', 'achievements', 'photos'
        ]
        read_only_fields = ['id', 'created_at']


class StudentCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    username = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Student
        fields = [
            'student_id', 'department', 'grade',
            'enrollment_date', 'graduation_date', 'status',
            'first_name', 'last_name', 'username', 'email', 'phone'
        ]
    
    def validate_student_id(self, value):
        if Student.objects.filter(student_id=value).exists():
            raise serializers.ValidationError('学号已存在')
        return value
    
    def create(self, validated_data):
        # 提取用户相关数据
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name', '')
        username = validated_data.pop('username', None)
        email = validated_data.pop('email', '')
        phone = validated_data.pop('phone', '')
        
        # 如果没有提供用户名，使用学号作为用户名
        if not username:
            username = f"student_{validated_data['student_id']}"
        
        # 检查用户名是否已存在，如果存在则添加后缀
        from django.contrib.auth import get_user_model
        User = get_user_model()
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        
        # 创建用户
        user = User.objects.create_user(
            username=username,
            email=email if email else f"{username}@example.com",
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            user_type='student'  # 默认用户类型为学员
        )
        
        # 创建学员
        validated_data['user'] = user
        student = super().create(validated_data)
        
        return student


class StudentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'department', 'grade', 'enrollment_date',
            'graduation_date', 'status'
        ]


class StudentContactUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentContact
        fields = [
            'emergency_contact', 'emergency_phone', 'address',
            'parent_name', 'parent_phone'
        ]


class StudentAchievementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAchievement
        fields = [
            'student', 'achievement_type', 'title', 'description',
            'date_achieved', 'certificate_file'
        ]
