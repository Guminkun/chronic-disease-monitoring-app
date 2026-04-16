"""
导入医院化验单数据到 indicators 表
"""
import csv
import sys
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database import Base, engine
from app.models import Indicator

def check_and_add_columns():
    """检查并添加缺失的字段"""
    print("检查数据库表结构...")
    
    # 获取数据库连接
    conn = engine.connect()
    
    # 检查表是否存在
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'indicators'
    """))
    
    existing_columns = [row[0] for row in result]
    print(f"现有字段: {existing_columns}")
    
    # 需要添加的字段
    columns_to_add = []
    
    if 'abbreviation' not in existing_columns:
        columns_to_add.append("""
            ALTER TABLE indicators 
            ADD COLUMN abbreviation VARCHAR(50)
        """)
        print("需要添加字段: abbreviation")
    
    if 'clinical_significance' not in existing_columns:
        columns_to_add.append("""
            ALTER TABLE indicators 
            ADD COLUMN clinical_significance TEXT
        """)
        print("需要添加字段: clinical_significance")
    
    # 执行添加字段的SQL
    if columns_to_add:
        print("\n开始添加缺失字段...")
        for sql in columns_to_add:
            try:
                conn.execute(text(sql))
                conn.commit()
                print(f"[OK] 成功执行: {sql[:50]}...")
            except Exception as e:
                print(f"[FAIL] 执行失败: {str(e)}")
                conn.rollback()
    else:
        print("\n[OK] 所有字段已存在，无需添加")
    
    conn.close()

def parse_value(value_str):
    """解析数值，如果无法解析返回None"""
    if not value_str or value_str.strip() == '' or value_str == '-':
        return None
    try:
        return Decimal(value_str.strip())
    except:
        return None

def import_data(csv_file_path):
    """导入CSV数据到数据库"""
    print(f"\n开始导入数据: {csv_file_path}")
    
    # 创建session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 读取CSV文件
        with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
            # 跳过BOM标记
            content = file.read()
            if content.startswith('\ufeff'):
                content = content[1:]
            
            # 使用csv模块解析
            reader = csv.DictReader(content.splitlines())
            
            count = 0
            skipped = 0
            
            for row in reader:
                try:
                    # 解析数据
                    category = row.get('化验单类别', '').strip()
                    name = row.get('检验项目', '').strip()
                    abbreviation = row.get('英文缩写', '').strip()
                    unit = row.get('单位', '').strip()
                    reference_text = row.get('参考范围(成人)', '').strip()
                    min_value = parse_value(row.get('最低值', ''))
                    max_value = parse_value(row.get('最高值', ''))
                    clinical_significance = row.get('临床意义', '').strip()
                    
                    # 跳过空名称的行
                    if not name:
                        skipped += 1
                        continue
                    
                    # 检查是否已存在（根据名称和类别）
                    existing = session.query(Indicator).filter_by(
                        name=name, 
                        category=category
                    ).first()
                    
                    if existing:
                        # 更新现有记录
                        existing.abbreviation = abbreviation
                        existing.unit = unit
                        existing.reference_min = min_value
                        existing.reference_max = max_value
                        existing.reference_text = reference_text
                        existing.clinical_significance = clinical_significance
                        print(f"更新: {name} ({category})")
                    else:
                        # 创建新记录
                        indicator = Indicator(
                            name=name,
                            abbreviation=abbreviation,
                            unit=unit,
                            reference_min=min_value,
                            reference_max=max_value,
                            reference_text=reference_text,
                            category=category,
                            clinical_significance=clinical_significance
                        )
                        session.add(indicator)
                        print(f"新增: {name} ({category})")
                    
                    count += 1
                    
                    # 每100条提交一次
                    if count % 100 == 0:
                        session.commit()
                        print(f"已处理 {count} 条记录...")
                
                except Exception as e:
                    print(f"处理行失败: {row.get('检验项目', '未知')} - {str(e)}")
                    session.rollback()
            
            # 提交剩余记录
            session.commit()
            
            print(f"\n导入完成!")
            print(f"成功处理: {count} 条")
            print(f"跳过: {skipped} 条")
    
    except Exception as e:
        print(f"导入失败: {str(e)}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    # CSV文件路径
    csv_file = r"E:\BaiduNetdiskDownload\医院化验单数据_小程序用.csv"
    
    print("=" * 60)
    print("医院化验单数据导入工具")
    print("=" * 60)
    
    # 步骤1: 检查并添加字段
    check_and_add_columns()
    
    # 步骤2: 导入数据
    import_data(csv_file)
    
    print("\n" + "=" * 60)
    print("任务完成!")
    print("=" * 60)
