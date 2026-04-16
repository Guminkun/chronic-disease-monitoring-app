"""
数据库迁移脚本：为 medication_logs 表添加 member_id 字段
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from sqlalchemy import text

def migrate():
    """添加 member_id 字段到 medication_logs 表"""
    
    with engine.connect() as conn:
        # 检查字段是否已存在
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'medication_logs' 
            AND column_name = 'member_id'
        """))
        
        if result.fetchone():
            print("member_id 字段已存在，无需迁移")
            return
        
        # 添加 member_id 字段
        print("正在添加 member_id 字段...")
        conn.execute(text("""
            ALTER TABLE medication_logs 
            ADD COLUMN member_id UUID REFERENCES members(id) ON DELETE CASCADE
        """))
        
        # 创建索引
        print("正在创建索引...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_medication_logs_member_id 
            ON medication_logs(member_id)
        """))
        
        conn.commit()
        print("迁移完成：medication_logs 表已添加 member_id 字段")

if __name__ == "__main__":
    migrate()
