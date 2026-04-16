from sqlalchemy import create_engine, text
import os

# 从环境变量或直接硬编码测试 (根据 .env)
DATABASE_URL = "postgresql://test:Psbc%401234@192.168.88.205:5432/testdb"

def fix_disease_schema():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # 检查 diseases 表的列
            query = text("SELECT column_name FROM information_schema.columns WHERE table_name = 'diseases'")
            result = conn.execute(query).fetchall()
            columns = [row[0] for row in result]
            print(f"Current columns in 'diseases': {columns}")
            
            if 'code' not in columns:
                print("Missing column: code")
                # 添加 code 列
                alter_query = text("ALTER TABLE diseases ADD COLUMN code VARCHAR(50)")
                conn.execute(alter_query)
                # 添加唯一约束 (可选，但模型中有 unique=True)
                # alter_unique = text("ALTER TABLE diseases ADD CONSTRAINT diseases_code_key UNIQUE (code)")
                # conn.execute(alter_unique)
                conn.commit()
                print("Column 'code' added successfully.")
            else:
                print("Column 'code' already exists.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_disease_schema()
