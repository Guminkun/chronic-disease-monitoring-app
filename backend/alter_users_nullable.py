"""
修改 users 表，允许 phone 和 password_hash 为空（支持微信登录）
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def migrate():
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("错误: 未找到DATABASE_URL环境变量")
        return
    
    print(f"连接数据库...")
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("修改 phone 列约束，允许为空...")
        cursor.execute("ALTER TABLE users ALTER COLUMN phone DROP NOT NULL")
        
        print("修改 password_hash 列约束，允许为空...")
        cursor.execute("ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL")
        
        conn.commit()
        print("迁移完成!")
        
        cursor.execute("""
            SELECT column_name, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name IN ('phone', 'password_hash')
        """)
        for row in cursor.fetchall():
            print(f"  {row[0]}: nullable={row[1]}")
        
    except Exception as e:
        print(f"迁移错误: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate()
