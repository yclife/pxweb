from django.shortcuts import render


def index(request):
    """主页视图"""
    return render(request, 'index.html')


def student_api_demo(request):
    """学员管理API演示页面"""
    return render(request, 'student_demo.html')
