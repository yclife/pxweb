import requests
import json

# 登录获取token
login_url = "http://localhost:8000/api/auth/login/"
login_data = {
    "username": "testuser",
    "password": "testpass123"
}

response = requests.post(login_url, json=login_data)
if response.status_code == 200:
    token_data = response.json()
    access_token = token_data['access']
    print(f"Access Token: {access_token}")
    
    # 使用新token测试创建学员
    create_url = "http://localhost:8000/api/students/"
    student_data = {
        "student_id": "S002",
        "first_name": "小明",
        "last_name": "张",
        "email": "xiaoming@example.com",
        "phone": "13800138000",
        "department": "计算机科学",
        "grade": "2023",
        "enrollment_date": "2023-09-01",
        "graduation_date": "2027-06-30",
        "status": "active"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    create_response = requests.post(create_url, json=student_data, headers=headers)
    print(f"\n创建学员状态码: {create_response.status_code}")
    print(f"创建学员响应: {create_response.text}")
else:
    print(f"登录失败: {response.status_code}")
    print(f"响应: {response.text}")
