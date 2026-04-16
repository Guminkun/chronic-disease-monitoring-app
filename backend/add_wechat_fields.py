"""
添加微信登录相关字段到users表
"""
import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), 'sql_app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'wechat_openid' not in columns:
            print("Adding wechat_openid column...")
            cursor.execute("ALTER TABLE users ADD COLUMN wechat_openid VARCHAR(100)")
        
        if 'wechat_unionid' not in columns:
            print("Adding wechat_unionid column...")
            cursor.execute("ALTER TABLE users ADD COLUMN wechat_unionid VARCHAR(100)")
        
        if 'wechat_nickname' not in columns:
            print("Adding wechat_nickname column...")
            cursor.execute("ALTER TABLE users ADD COLUMN wechat_nickname VARCHAR(100)")
        
        if 'wechat_avatar' not in columns:
            print("Adding wechat_avatar column...")
            cursor.execute("ALTER TABLE users ADD COLUMN wechat_avatar VARCHAR(500)")
        
        print("Creating indexes...")
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_users_wechat_openid ON users(wechat_openid)")
        except Exception as e:
            print(f"Index on wechat_openid might already exist: {e}")
        
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_users_wechat_unionid ON users(wechat_unionid)")
        except Exception as e:
            print(f"Index on wechat_unionid might already exist: {e}")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
