import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
from docx import Document
import re

def get_category_by_row(row_cells):
    first_cell = row_cells[0]
    mapping = {
        "白细胞系统（感染 / 造血相关）": "血常规",
        "干化学检测项": "尿常规",
        "一般性状": "粪便常规",
        "凝血酶原时间": "凝血功能",
        "谷丙转氨酶": "肝功能",
        "血肌酐": "肾功能",
        "血钾": "电解质",
        "总胆固醇": "血脂",
        "空腹血糖": "血糖",
        "肌酸激酶": "心肌酶谱",
        "肌钙蛋白 I": "心肌标志物",
        "促甲状腺激素": "甲状腺功能",
        "促卵泡生成素": "性激素"
    }
    if first_cell in mapping:
        return mapping[first_cell]
    return None

def parse_reference(ref_str):
    """
    Parse reference string to min, max.
    Examples:
    "3.5~5.5" -> 3.5, 5.5
    "<5.2" -> None, 5.2
    ">1.04" -> 1.04, None
    "0~40" -> 0, 40
    "阴性" -> None, None
    """
    if not ref_str or ref_str.strip() == "-":
        return None, None
    
    ref_str = ref_str.strip()
    
    # Try simple range "A~B"
    if "~" in ref_str:
        parts = ref_str.split("~")
        if len(parts) == 2:
            try:
                return float(parts[0]), float(parts[1])
            except:
                pass
                
    # Try "<X"
    if ref_str.startswith("＜") or ref_str.startswith("<"):
        try:
            val = float(ref_str[1:])
            return None, val
        except:
            pass
            
    # Try ">X"
    if ref_str.startswith("＞") or ref_str.startswith(">"):
        try:
            val = float(ref_str[1:])
            return val, None
        except:
            pass
            
    # Try "≥X"
    if ref_str.startswith("≥"):
        try:
            val = float(ref_str[1:])
            return val, None
        except:
            pass
            
    return None, None

def seed_indicators():
    db = SessionLocal()
    
    # Clear existing indicators
    db.query(models.Indicator).delete()
    db.commit()
    print("Cleared existing indicators.")
    
    file_path = r"C:\Users\郭帅\Desktop\chronic-disease-monitoring-app\指标项.docx"
    doc = Document(file_path)
    
    count = 0
    
    # Global category state since tables might be merged
    current_category = "其他"
    
    for table in doc.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            
            # Check for header-like rows to skip
            if "简称" in cells or "单位" in cells:
                continue
                
            # Check if this row defines a new category
            new_cat = get_category_by_row(cells)
            if new_cat:
                current_category = new_cat
                # Some section headers are just headers, not data
                if cells[0] in ["白细胞系统（感染 / 造血相关）", "干化学检测项", "一般性状"]:
                    continue
            
            if not any(cells):
                continue
                
            # Process data
            items = []
            
            # Logic for different column layouts
            if len(cells) == 4:
                items.append({"name": cells[0], "unit": cells[2], "ref": cells[3]})
            elif len(cells) >= 7:
                 # Duplicated or 8-col layout
                 # Check if it's the stool/urine table special case (Category column at index 0)
                 if current_category in ["粪便常规", "尿常规"] and len(cells) >= 8:
                     # "一般性状 | 粪便颜色 | ..." -> Name at 1
                     # "显微镜镜检 | 白细胞 | ..." -> Name at 1
                     # "尿沉渣定量项 | 红细胞计数 | ..." -> Name at 1
                     name_idx = 1
                     unit_idx = 5
                     ref_idx = 7
                     items.append({"name": cells[name_idx], "unit": cells[unit_idx], "ref": cells[ref_idx]})
                 else:
                     # Duplicated columns: 0, 2, 4, 6
                     items.append({"name": cells[0], "unit": cells[4], "ref": cells[6]})
            elif len(cells) == 5:
                # Sex hormones: Item | Abbr | Unit | Male | Female
                ref = f"男: {cells[3]}; 女: {cells[4]}"
                items.append({"name": cells[0], "unit": cells[2], "ref": ref})
            
            for item in items:
                name = item["name"]
                if name == "-" or not name:
                    continue
                if name in ["项目", "白细胞系统（感染 / 造血相关）", "红细胞系统（贫血相关）", "血小板系统（凝血 / 出血相关）", "干化学检测项", "尿沉渣定量项", "一般性状", "显微镜镜检", "隐血试验"]:
                     continue

                # Check duplication
                existing = db.query(models.Indicator).filter(models.Indicator.name == name).first()
                if existing:
                    continue
                
                min_val, max_val = parse_reference(item["ref"])
                
                indicator = models.Indicator(
                    name=name,
                    unit=item["unit"] if item["unit"] != "-" else None,
                    reference_min=min_val,
                    reference_max=max_val,
                    reference_text=item["ref"],
                    category=current_category
                )
                db.add(indicator)
                count += 1
                print(f"Added: {name} [{current_category}]")

    db.commit()
    print(f"Successfully added {count} indicators.")
    db.close()

if __name__ == "__main__":
    seed_indicators()
