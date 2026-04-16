"""
添加微信登录相关字段到users表 (PostgreSQL版本)
"""
import psycopg2
from psycopg2 import sql
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
        
        print("检查现有列...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users'
        """)
        columns = [row[0] for row in cursor.fetchall()]
        print(f"现有列: {columns}")
        
        if 'wechat_openid' not in columns:
            print("添加 wechat_openid 列...")
            cursor.execute("ALTER TABLE users ADD COLUMN wechat_openid VARCHAR(100)")
        
        if 'wechat_unionid' not in columns:
            print("添加 wechat_unionid 列...")
            cursor.execute("ALTER TABLE users ADD COLUMN wechat_unionid VARCHAR(100)")
        
        if 'wechat_nickname' not in columns:
            print("添加 wechat_nickname 列...")
            cursor.execute("ALTER TABLE users ADD COLUMN wechat_nickname VARCHAR(100)")
        
        if 'wechat_avatar' not in columns:
            print("添加 wechat_avatar 列...")
            cursor.execute("ALTER TABLE users ADD COLUMN wechat_avatar VARCHAR(500)")
        
        print("创建索引...")
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_users_wechat_openid ON users(wechat_openid)")
        except Exception as e:
            print(f"索引创建提示: {e}")
        
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_users_wechat_unionid ON users(wechat_unionid)")
        except Exception as e:
            print(f"索引创建提示: {e}")
        
        conn.commit()
        print("✓ 迁移完成!")
        
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users'
        """)
        columns = [row[0] for row in cursor.fetchall()]
        print(f"更新后的列: {columns}")
        
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
