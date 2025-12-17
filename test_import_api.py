import requests
import json
import os

# 从get_token.py获取token
def get_token():
    login_url = "http://localhost:8000/api/auth/login/"
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    response = requests.post(login_url, json=login_data)
    if response.status_code == 200:
        token_data = response.json()
        return token_data['access']
    else:
        print(f"登录失败: {response.status_code}")
        print(f"响应: {response.text}")
        return None

# 测试导入功能
def test_import():
    # 获取token
    token = get_token()
    if not token:
        print("无法获取token，测试终止")
        return
    
    print(f"获取到的Token: {token[:20]}...")
    
    # 准备请求头
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 准备文件
    import pandas as pd
    
    # 创建测试数据
    test_data = [
        ['学号', '姓名', '姓氏', '用户名', '邮箱', '电话', '院系', '年级', '入学日期', '毕业日期', '状态'],
        ['IMPORT001', '导入测试1', '导入', 'import1', 'import1@example.com', '13800138111', '计算机学院', '2023级', '2023-09-01', '2027-06-30', '在读'],
        ['IMPORT002', '导入测试2', '导入', 'import2', 'import2@example.com', '13800138112', '软件学院', '2023级', '2023-09-01', '2027-06-30', '在读']
    ]
    
    # 创建DataFrame并保存为Excel
    df = pd.DataFrame(test_data[1:], columns=test_data[0])
    test_file = 'test_import_api.xlsx'
    df.to_excel(test_file, index=False)
    
    print(f"创建测试文件: {test_file}")
    print("测试数据:")
    print(df)
    
    # 发送导入请求
    import_url = "http://localhost:8000/api/students/import/"
    
    with open(test_file, 'rb') as f:
        files = {'file': (test_file, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        response = requests.post(import_url, headers=headers, files=files)
    
    # 清理测试文件
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print(f"\n导入响应状态码: {response.status_code}")
    print(f"导入响应内容: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n导入结果:")
        print(f"消息: {result.get('message')}")
        print(f"总计: {result.get('results', {}).get('total', 0)}")
        print(f"成功: {result.get('results', {}).get('success', 0)}")
        print(f"失败: {result.get('results', {}).get('failed', 0)}")
        
        if result.get('results', {}).get('errors'):
            print("\n错误详情:")
            for error in result['results']['errors']:
                print(f"  第{error['row']}行 - 学号{error['student_id']}: {error['error']}")
    
    # 验证数据是否写入数据库
    print("\n验证数据库写入...")
    verify_url = "http://localhost:8000/api/students/"
    verify_response = requests.get(verify_url, headers=headers)
    
    if verify_response.status_code == 200:
        students_data = verify_response.json()
        print(f"当前学员总数: {students_data.get('pagination', {}).get('total_count', 0)}")
        
        # 检查导入的学员是否存在
        import_students = ['IMPORT001', 'IMPORT002']
        for student_id in import_students:
            search_url = f"http://localhost:8000/api/students/?search={student_id}"
            search_response = requests.get(search_url, headers=headers)
            if search_response.status_code == 200:
                search_data = search_response.json()
                if search_data.get('data'):
                    print(f"学员 {student_id} 已成功写入数据库")
                else:
                    print(f"学员 {student_id} 未找到")
            else:
                print(f"搜索学员 {student_id} 失败: {search_response.status_code}")

if __name__ == "__main__":
    test_import()
