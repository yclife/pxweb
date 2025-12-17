from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # 学员管理
    path('students/', views.StudentListView.as_view(), name='student-list'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    
    # 学员联系信息
    path('students/<int:student_id>/contact/', views.StudentContactView.as_view(), name='student-contact'),
    
    # 学员成就管理
    path('students/<int:student_id>/achievements/', views.StudentAchievementListView.as_view(), name='student-achievement-list'),
    path('achievements/<int:achievement_id>/', views.StudentAchievementDetailView.as_view(), name='student-achievement-detail'),
    
    # 统计信息
    path('students/stats/', views.student_stats, name='student-stats'),
    
    # 导入导出功能
    path('students/export/', views.StudentExportView.as_view(), name='student-export'),
    path('students/import/', views.StudentImportView.as_view(), name='student-import'),
    
    # 学员相片管理
    path('students/<int:student_id>/photos/', views.StudentPhotoListView.as_view(), name='student-photo-list'),
    path('photos/<int:photo_id>/', views.StudentPhotoDetailView.as_view(), name='student-photo-detail'),
    path('students/<int:student_id>/photos/batch-upload/', views.StudentPhotoBatchUploadView.as_view(), name='student-photo-batch-upload'),
]
