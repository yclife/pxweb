from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from django.http import HttpResponse
import pandas as pd
import io
import json
from datetime import datetime
from .models import Student, StudentContact, StudentAchievement, StudentPhoto
from .serializers import (
    StudentSerializer, StudentCreateSerializer, StudentUpdateSerializer,
    StudentContactUpdateSerializer, StudentAchievementSerializer,
    StudentAchievementCreateSerializer, StudentPhotoSerializer,
    StudentPhotoCreateSerializer
)


class StudentListView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # 恢复需要认证
    
    def get(self, request):
        # 支持搜索和过滤
        search = request.query_params.get('search', '')
        status_filter = request.query_params.get('status', '')
        department_filter = request.query_params.get('department', '')
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)
        
        students = Student.objects.all()
        
        # 搜索功能
        if search:
            students = students.filter(
                Q(student_id__icontains=search) |
                Q(user__username__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(department__icontains=search)
            )
        
        # 状态过滤
        if status_filter:
            students = students.filter(status=status_filter)
        
        # 院系过滤
        if department_filter:
            students = students.filter(department__icontains=department_filter)
        
        # 分页
        try:
            page = int(page)
            page_size = int(page_size)
        except ValueError:
            page = 1
            page_size = 20
            
        total_count = students.count()
        total_pages = (total_count + page_size - 1) // page_size
        
        start = (page - 1) * page_size
        end = start + page_size
        students = students[start:end]
        
        serializer = StudentSerializer(students, many=True)
        return Response({
            'data': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': total_pages
            }
        })
    
    def post(self, request):
        serializer = StudentCreateSerializer(data=request.data)
        if serializer.is_valid():
            student = serializer.save()
            # 创建学员联系信息记录
            StudentContact.objects.create(student=student)
            return Response(
                StudentSerializer(student).data,
                status=status.HTTP_201_CREATED
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentPhotoListView(APIView):
    """学员相片列表和上传"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, student_id):
        """获取学员相片列表"""
        try:
            student = Student.objects.get(pk=student_id)
            photos = student.photos.all()
            serializer = StudentPhotoSerializer(
                photos, 
                many=True,
                context={'request': request}
            )
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(
                {'error': '学员不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def post(self, request, student_id):
        """上传学员相片"""
        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return Response(
                {'error': '学员不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 检查是否有文件上传
        if 'photo' not in request.FILES:
            return Response(
                {'error': '请选择相片文件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查文件类型
        photo_file = request.FILES['photo']
        if not photo_file.content_type.startswith('image/'):
            return Response(
                {'error': f'文件类型必须是图片，当前类型: {photo_file.content_type}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查文件大小（限制为5MB）
        if photo_file.size > 5 * 1024 * 1024:
            return Response(
                {'error': f'文件大小不能超过5MB，当前大小: {photo_file.size} bytes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 准备数据
        data = request.data.copy()
        data['student'] = student.id
        
        serializer = StudentPhotoCreateSerializer(data=data)
        if serializer.is_valid():
            photo = serializer.save()
            photo_serializer = StudentPhotoSerializer(
                photo,
                context={'request': request}
            )
            return Response(
                photo_serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        # 返回详细的验证错误
        return Response({
            'error': '数据验证失败',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class StudentPhotoDetailView(APIView):
    """学员相片详情和删除"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, photo_id):
        try:
            return StudentPhoto.objects.get(pk=photo_id)
        except StudentPhoto.DoesNotExist:
            return None
    
    def get(self, request, photo_id):
        """获取相片详情"""
        photo = self.get_object(photo_id)
        if photo is None:
            return Response(
                {'error': '相片不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = StudentPhotoSerializer(
            photo,
            context={'request': request}
        )
        return Response(serializer.data)
    
    def delete(self, request, photo_id):
        """删除相片"""
        photo = self.get_object(photo_id)
        if photo is None:
            return Response(
                {'error': '相片不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def patch(self, request, photo_id):
        """更新相片信息（如设置为主相片）"""
        photo = self.get_object(photo_id)
        if photo is None:
            return Response(
                {'error': '相片不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 如果设置为primary，取消其他相片的primary状态
        if request.data.get('is_primary', False):
            StudentPhoto.objects.filter(
                student=photo.student, 
                is_primary=True
            ).update(is_primary=False)
        
        serializer = StudentPhotoSerializer(
            photo, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentPhotoBatchUploadView(APIView):
    """批量上传学员相片"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, student_id):
        """批量上传相片"""
        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return Response(
                {'error': '学员不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 检查是否有文件上传
        if 'photos' not in request.FILES:
            return Response(
                {'error': '请选择相片文件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        photos = request.FILES.getlist('photos')
        results = {
            'total': len(photos),
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for index, photo_file in enumerate(photos):
            try:
                # 检查文件类型
                if not photo_file.content_type.startswith('image/'):
                    raise ValueError('文件类型必须是图片')
                
                # 检查文件大小（限制为5MB）
                if photo_file.size > 5 * 1024 * 1024:
                    raise ValueError('文件大小不能超过5MB')
                
                # 创建相片记录
                photo = StudentPhoto.objects.create(
                    student=student,
                    photo=photo_file,
                    description=f"相片 {index + 1}"
                )
                results['success'] += 1
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'index': index,
                    'filename': photo_file.name,
                    'error': str(e)
                })
        
        return Response({
            'message': f'批量上传完成，成功: {results["success"]}, 失败: {results["failed"]}',
            'results': results
        })


class StudentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return None
    
    def get(self, request, pk):
        student = self.get_object(pk)
        if student is None:
            return Response(
                {'error': '学员不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = StudentSerializer(student)
        return Response(serializer.data)
    
    def put(self, request, pk):
        student = self.get_object(pk)
        if student is None:
            return Response(
                {'error': '学员不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = StudentUpdateSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(StudentSerializer(student).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        student = self.get_object(pk)
        if student is None:
            return Response(
                {'error': '学员不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentContactView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, student_id):
        try:
            student = Student.objects.get(pk=student_id)
            return StudentContact.objects.get(student=student)
        except (Student.DoesNotExist, StudentContact.DoesNotExist):
            return None
    
    def get(self, request, student_id):
        contact_info = self.get_object(student_id)
        if contact_info is None:
            return Response(
                {'error': '学员联系信息不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = StudentContactUpdateSerializer(contact_info)
        return Response(serializer.data)
    
    def put(self, request, student_id):
        contact_info = self.get_object(student_id)
        if contact_info is None:
            return Response(
                {'error': '学员联系信息不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = StudentContactUpdateSerializer(
            contact_info, 
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentAchievementListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, student_id):
        try:
            student = Student.objects.get(pk=student_id)
            achievements = student.achievements.all()
            serializer = StudentAchievementSerializer(achievements, many=True)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(
                {'error': '学员不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def post(self, request, student_id):
        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return Response(
                {'error': '学员不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        data = request.data.copy()
        data['student'] = student.id
        
        serializer = StudentAchievementCreateSerializer(data=data)
        if serializer.is_valid():
            achievement = serializer.save()
            return Response(
                StudentAchievementSerializer(achievement).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentAchievementDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, achievement_id):
        try:
            return StudentAchievement.objects.get(pk=achievement_id)
        except StudentAchievement.DoesNotExist:
            return None
    
    def get(self, request, achievement_id):
        achievement = self.get_object(achievement_id)
        if achievement is None:
            return Response(
                {'error': '成就记录不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = StudentAchievementSerializer(achievement)
        return Response(serializer.data)
    
    def put(self, request, achievement_id):
        achievement = self.get_object(achievement_id)
        if achievement is None:
            return Response(
                {'error': '成就记录不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = StudentAchievementSerializer(
            achievement, 
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, achievement_id):
        achievement = self.get_object(achievement_id)
        if achievement is None:
            return Response(
                {'error': '成就记录不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        achievement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def student_stats(request):
    """学员统计信息"""
    total_students = Student.objects.count()
    active_students = Student.objects.filter(status='active').count()
    graduated_students = Student.objects.filter(status='graduated').count()
    
    return Response({
        'total_students': total_students,
        'active_students': active_students,
        'graduated_students': graduated_students
    })


class StudentExportView(APIView):
    """导出学员数据为Excel文件"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # 获取所有学员数据
        students = Student.objects.all().select_related('user')
        
        # 准备数据
        data = []
        for student in students:
            data.append({
                '学号': student.student_id,
                '姓名': student.user.first_name,
                '姓氏': student.user.last_name,
                '用户名': student.user.username,
                '邮箱': student.user.email,
                '电话': student.user.phone,
                '院系': student.department,
                '年级': student.grade,
                '入学日期': student.enrollment_date.strftime('%Y-%m-%d') if student.enrollment_date else '',
                '毕业日期': student.graduation_date.strftime('%Y-%m-%d') if student.graduation_date else '',
                '状态': student.get_status_display(),
                '创建时间': student.created_at.strftime('%Y-%m-%d %H:%M:%S') if student.created_at else '',
            })
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 创建Excel文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='学员数据', index=False)
        
        # 准备HTTP响应
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="students_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        
        return response


class StudentImportView(APIView):
    """导入Excel文件批量创建学员"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # 检查是否有文件上传
        if 'file' not in request.FILES:
            return Response(
                {'error': '请上传文件'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        
        # 检查文件类型
        if not file.name.endswith(('.xlsx', '.xls')):
            return Response(
                {'error': '只支持Excel文件 (.xlsx, .xls)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 读取Excel文件
            df = pd.read_excel(file)
            
            # 检查必要的列
            required_columns = ['学号', '姓名']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response(
                    {'error': f'Excel文件缺少必要的列: {", ".join(missing_columns)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 处理数据
            results = {
                'total': len(df),
                'success': 0,
                'failed': 0,
                'errors': []
            }
            
            for index, row in df.iterrows():
                try:
                    # 准备数据
                    student_data = {
                        'student_id': str(row.get('学号', '')).strip(),
                        'first_name': str(row.get('姓名', '')).strip(),
                        'last_name': str(row.get('姓氏', '')).strip() if pd.notna(row.get('姓氏')) else '',
                        'username': str(row.get('用户名', '')).strip() if pd.notna(row.get('用户名')) else '',
                        'email': str(row.get('邮箱', '')).strip() if pd.notna(row.get('邮箱')) else '',
                        'phone': str(row.get('电话', '')).strip() if pd.notna(row.get('电话')) else '',
                        'department': str(row.get('院系', '')).strip() if pd.notna(row.get('院系')) else '',
                        'grade': str(row.get('年级', '')).strip() if pd.notna(row.get('年级')) else '',
                        'enrollment_date': self._parse_date(row.get('入学日期')) if pd.notna(row.get('入学日期')) else '',
                        'graduation_date': self._parse_date(row.get('毕业日期')) if pd.notna(row.get('毕业日期')) else '',
                        'status': self._map_status(str(row.get('状态', '')).strip()) if pd.notna(row.get('状态')) else 'active',
                    }
                    
                    # 验证必填字段
                    if not student_data['student_id']:
                        raise ValueError('学号不能为空')
                    if not student_data['first_name']:
                        raise ValueError('姓名不能为空')
                    
                    # 检查学号是否已存在
                    if Student.objects.filter(student_id=student_data['student_id']).exists():
                        raise ValueError(f'学号 {student_data["student_id"]} 已存在')
                    
                    # 调试：打印准备的数据
                    print(f"准备创建学员数据: {student_data}")
                    
                    # 创建学员
                    serializer = StudentCreateSerializer(data=student_data)
                    if serializer.is_valid():
                        student = serializer.save()
                        print(f"学员创建成功: {student.student_id} - {student.user.username}")
                        results['success'] += 1
                    else:
                        print(f"数据验证失败: {serializer.errors}")
                        raise ValueError(f'数据验证失败: {serializer.errors}')
                        
                except Exception as e:
                    results['failed'] += 1
                    error_msg = str(e)
                    print(f"导入第{index + 2}行失败: {error_msg}")
                    results['errors'].append({
                        'row': index + 2,  # Excel行号（从2开始，因为第一行是标题）
                        'student_id': str(row.get('学号', '')).strip() if pd.notna(row.get('学号')) else '未知',
                        'error': error_msg
                    })
            
            return Response({
                'message': f'导入完成，成功: {results["success"]}, 失败: {results["failed"]}',
                'results': results
            })
            
        except Exception as e:
            return Response(
                {'error': f'文件处理失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _map_status(self, status_str):
        """映射状态字符串到数据库值"""
        status_map = {
            '在读': 'active',
            '已毕业': 'graduated',
            '休学': 'suspended',
            '退学': 'dropped',
            'active': 'active',
            'graduated': 'graduated',
            'suspended': 'suspended',
            'dropped': 'dropped',
        }
        return status_map.get(status_str, 'active')
    
    def _parse_date(self, date_value):
        """解析日期值，支持多种格式"""
        if pd.isna(date_value):
            return ''
        
        # 如果已经是字符串，直接返回
        if isinstance(date_value, str):
            return date_value.strip()
        
        # 如果是pandas Timestamp，转换为字符串
        if isinstance(date_value, pd.Timestamp):
            return date_value.strftime('%Y-%m-%d')
        
        # 如果是datetime对象，转换为字符串
        if hasattr(date_value, 'strftime'):
            try:
                return date_value.strftime('%Y-%m-%d')
            except:
                return str(date_value)
        
        # 其他情况转换为字符串
        return str(date_value)
