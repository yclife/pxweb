import pymysql

# 数据库连接参数
host = 'localhost'
user = 'root'
password = '@jlzx123'
database = 'django_db'

try:
    # 连接到MySQL服务器（不指定数据库）
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password
    )
    
    with connection.cursor() as cursor:
        # 创建数据库（如果不存在）
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"Database '{database}' created or already exists.")
    
    connection.commit()
    print("Success!")
    
except pymysql.Error as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals() and connection:
        connection.close()
