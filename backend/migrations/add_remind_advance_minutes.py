"""
数据库迁移脚本：添加 remind_advance_minutes 字段到 medication_plans 表
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import sys

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://test:Psbc%401234@192.168.88.205:5432/testdb")

def migrate():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # 检查字段是否已存在
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='medication_plans' 
            AND column_name='remind_advance_minutes'
        """))
        
        if result.fetchone():
            print("字段 remind_advance_minutes 已存在，无需迁移")
            return
        
        # 添加字段
        conn.execute(text("""
            ALTER TABLE medication_plans 
            ADD COLUMN remind_advance_minutes INTEGER DEFAULT 5
        """))
        
        conn.commit()
        
        print("成功添加字段 remind_advance_minutes 到 medication_plans 表")
        print("默认值：5分钟")

if __name__ == "__main__":
    print("开始迁移...")
    migrate()
    print("迁移完成！")
