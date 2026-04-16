#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量导入药品数据 from multiple Excel files - 带字段长度截断
"""
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models import Medication

DATABASE_URL = "postgresql://test:Psbc%401234@192.168.88.205:5432/testdb"

MAX_LEN = {
    'title': 300, 'title_url': 500, 'number': 100, 'r3': 200,
    'generic_name': 200, 'trade_name': 200, 'pinyin': 300,
    'approval_number': 100, 'category': 100, 'manufacturer': 200,
    'drug_nature': 100, 'related_diseases': 5000, 'properties': 5000,
    'main_ingredients': 5000, 'indications': 10000, 'specification': 200,
    'adverse_reactions': 10000, 'usage_dosage': 10000, 'contraindications': 5000,
    'precautions': 5000, 'pregnancy_lactation': 5000, 'pediatric_use': 5000,
    'geriatric_use': 5000, 'drug_interactions': 5000, 'pharmacology_toxicology': 10000,
    'pharmacokinetics': 10000, 'storage': 2000, 'expiry_period': 200,
    'therapeutic_system_category': 100, 'therapeutic_system_subcategory': 100
}

def truncate(s, max_len):
    if s is None:
        return None
    s = str(s)
    if len(s) > max_len:
        return s[:max_len]
    return s

def import_medications():
    print("开始批量导入药品数据...")
    
    files = [
        "E:/BaiduNetdiskDownload/二级分类医药数据/药品说明书数据库_医药数据查询(2)_二级分类.xlsx",
        "E:/BaiduNetdiskDownload/二级分类医药数据/药品说明书数据库_医药数据查询(3)_二级分类.xlsx",
        "E:/BaiduNetdiskDownload/二级分类医药数据/药品说明书数据库_医药数据查询(4)_二级分类.xlsx",
        "E:/BaiduNetdiskDownload/二级分类医药数据/药品说明书数据库_医药数据查询(5)_二级分类.xlsx",
        "E:/BaiduNetdiskDownload/二级分类医药数据/药品说明书数据库_医药数据查询(6)_二级分类.xlsx",
        "E:/BaiduNetdiskDownload/二级分类医药数据/药品说明书数据库_医药数据查询(7)_二级分类.xlsx"
    ]
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    total_success = 0
    total_skip = 0
    total_error = 0
    
    def get_val_by_idx(row, idx):
        if idx >= len(row):
            return None
        val = row.iloc[idx]
        if pd.isna(val):
            return None
        s = str(val).strip()
        return None if s == 'nan' or s == '' else s
    
    for file_idx, excel_path in enumerate(files):
        print(f"\n=== 处理文件 {file_idx + 1}/6: {os.path.basename(excel_path)} ===")
        
        df = pd.read_excel(excel_path)
        print(f"读取到 {len(df)} 条记录")
        
        success_count = 0
        skip_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                with session.no_autoflush:
                    generic_name = get_val_by_idx(row, 4)
                    approval_number = get_val_by_idx(row, 7)
                    
                    if not generic_name:
                        skip_count += 1
                        continue
                    
                    query = session.query(Medication).filter(
                        Medication.generic_name == generic_name
                    )
                    if approval_number:
                        query = query.filter(Medication.approval_number == approval_number)
                    
                    exists = query.first()
                    
                    if exists:
                        exists.therapeutic_system_category = truncate(get_val_by_idx(row, 28), MAX_LEN['therapeutic_system_category'])
                        exists.therapeutic_system_subcategory = truncate(get_val_by_idx(row, 29), MAX_LEN['therapeutic_system_subcategory'])
                        skip_count += 1
                        continue
                    
                    med = Medication(
                        title=truncate(get_val_by_idx(row, 0), MAX_LEN['title']),
                        title_url=truncate(get_val_by_idx(row, 1), MAX_LEN['title_url']),
                        number=truncate(get_val_by_idx(row, 2), MAX_LEN['number']),
                        r3=truncate(get_val_by_idx(row, 3), MAX_LEN['r3']),
                        generic_name=truncate(generic_name, MAX_LEN['generic_name']),
                        trade_name=truncate(get_val_by_idx(row, 5), MAX_LEN['trade_name']),
                        pinyin=truncate(get_val_by_idx(row, 6), MAX_LEN['pinyin']),
                        approval_number=truncate(approval_number, MAX_LEN['approval_number']),
                        category=truncate(get_val_by_idx(row, 8), MAX_LEN['category']),
                        manufacturer=truncate(get_val_by_idx(row, 9), MAX_LEN['manufacturer']),
                        therapeutic_system_category=truncate(get_val_by_idx(row, 28), MAX_LEN['therapeutic_system_category']),
                        therapeutic_system_subcategory=truncate(get_val_by_idx(row, 29), MAX_LEN['therapeutic_system_subcategory']),
                        drug_nature=truncate(get_val_by_idx(row, 10), MAX_LEN['drug_nature']),
                        related_diseases=truncate(get_val_by_idx(row, 11), MAX_LEN['related_diseases']),
                        properties=truncate(get_val_by_idx(row, 12), MAX_LEN['properties']),
                        main_ingredients=truncate(get_val_by_idx(row, 13), MAX_LEN['main_ingredients']),
                        indications=truncate(get_val_by_idx(row, 14), MAX_LEN['indications']),
                        specification=truncate(get_val_by_idx(row, 15), MAX_LEN['specification']),
                        adverse_reactions=truncate(get_val_by_idx(row, 16), MAX_LEN['adverse_reactions']),
                        usage_dosage=truncate(get_val_by_idx(row, 17), MAX_LEN['usage_dosage']),
                        contraindications=truncate(get_val_by_idx(row, 18), MAX_LEN['contraindications']),
                        precautions=truncate(get_val_by_idx(row, 19), MAX_LEN['precautions']),
                        pregnancy_lactation=truncate(get_val_by_idx(row, 20), MAX_LEN['pregnancy_lactation']),
                        pediatric_use=truncate(get_val_by_idx(row, 21), MAX_LEN['pediatric_use']),
                        geriatric_use=truncate(get_val_by_idx(row, 22), MAX_LEN['geriatric_use']),
                        drug_interactions=truncate(get_val_by_idx(row, 23), MAX_LEN['drug_interactions']),
                        pharmacology_toxicology=truncate(get_val_by_idx(row, 24), MAX_LEN['pharmacology_toxicology']),
                        pharmacokinetics=truncate(get_val_by_idx(row, 25), MAX_LEN['pharmacokinetics']),
                        storage=truncate(get_val_by_idx(row, 26), MAX_LEN['storage']),
                        expiry_period=truncate(get_val_by_idx(row, 27), MAX_LEN['expiry_period']),
                        status='active'
                    )
                    
                    session.add(med)
                    success_count += 1
                    
                    if (index + 1) % 2000 == 0:
                        session.commit()
                        print(f"  已处理 {index + 1} 条...")
                        
            except Exception as e:
                error_count += 1
                if error_count <= 3:
                    print(f"  Error at row {index + 2}: {e}")
        
        try:
            session.commit()
        except:
            session.rollback()
        print(f"  成功: {success_count}, 跳过: {skip_count}, 失败: {error_count}")
        
        total_success += success_count
        total_skip += skip_count
        total_error += error_count
    
    session.close()
    
    print(f"\n========== 全部导入完成! ==========")
    print(f"总成功: {total_success}")
    print(f"总跳过(已存在): {total_skip}")
    print(f"总失败: {total_error}")

if __name__ == "__main__":
    import_medications()
