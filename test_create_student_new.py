import requests
import json

url = "http://localhost:8000/api/students/"

# 测试新的创建学员API
data = {
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
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY0Njg0NDYwLCJpYXQiOjE3NjQ2ODQxNjAsImp0aSI6IjJhYzc5OGQxYzFiODQ2YTE4MjE4MDM1YjlmNGUzYWYwIiwidXNlcl9pZCI6M30.fdo-TcTgtfguluZnOcFvjdZogti0-l5oRVeiBjfcsMQ"
}

print("测试创建学员（带认证）")
response = requests.post(url, json=data, headers=headers)
print(f"状态码: {response.status_code}")
print(f"响应: {response.text}")

# 测试不带认证
print("\n测试创建学员（不带认证）")
response2 = requests.post(url, json=data)
print(f"状态码: {response2.status_code}")
print(f"响应: {response2.text}")
