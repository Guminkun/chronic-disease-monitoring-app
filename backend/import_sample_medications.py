"""
导入示例药品数据
用于测试药品搜索功能
"""
from app.database import SessionLocal
from app.models import Medication

# 示例药品数据
sample_medications = [
    {
        "title": "阿莫西林胶囊",
        "generic_name": "阿莫西林",
        "trade_name": "阿莫仙",
        "pinyin": "A Mo Xi Lin",
        "approval_number": "国药准字H20052345",
        "category": "化学药品",
        "manufacturer": "珠海联邦制药股份有限公司",
        "properties": "本品为胶囊剂",
        "specification": "0.25g*24粒",
        "indications": "适用于敏感菌所致的各种感染",
        "adverse_reactions": "恶心、呕吐、腹泻",
        "usage_dosage": "口服。成人一次0.5g，每6-8小时1次",
        "status": "active"
    },
    {
        "title": "头孢克肟分散片",
        "generic_name": "头孢克肟",
        "trade_name": "世福素",
        "pinyin": "Tou Bao Ke Wo",
        "approval_number": "国药准字H20050749",
        "category": "化学药品",
        "manufacturer": "广州白云山制药股份有限公司",
        "properties": "本品为白色或类白色片",
        "specification": "0.1g*6片",
        "indications": "用于治疗呼吸道感染、泌尿道感染等",
        "adverse_reactions": "腹泻、腹痛、皮疹",
        "usage_dosage": "口服。成人及体重30kg以上儿童，每次0.1g，一日2次",
        "status": "active"
    },
    {
        "title": "布洛芬缓释胶囊",
        "generic_name": "布洛芬",
        "trade_name": "芬必得",
        "pinyin": "Bu Luo Fen",
        "approval_number": "国药准字H10900089",
        "category": "化学药品",
        "manufacturer": "中美天津史克制药有限公司",
        "properties": "本品为缓释胶囊",
        "specification": "0.3g*20粒",
        "indications": "用于缓解轻至中度疼痛，如关节痛、肌肉痛、头痛等",
        "adverse_reactions": "胃肠道不适、头痛、耳鸣",
        "usage_dosage": "口服。成人一次1粒，一日2次",
        "status": "active"
    },
    {
        "title": "阿司匹林肠溶片",
        "generic_name": "阿司匹林",
        "trade_name": "拜阿司匹灵",
        "pinyin": "A Si Pi Lin",
        "approval_number": "国药准字J20130007",
        "category": "化学药品",
        "manufacturer": "拜耳医药保健有限公司",
        "properties": "本品为肠溶包衣片",
        "specification": "100mg*30片",
        "indications": "用于预防心脑血管疾病",
        "adverse_reactions": "胃肠道出血、溃疡",
        "usage_dosage": "口服。一日1次，一次1片",
        "status": "active"
    },
    {
        "title": "氯沙坦钾片",
        "generic_name": "氯沙坦钾",
        "trade_name": "科素亚",
        "pinyin": "Lv Sha Tan Jia",
        "approval_number": "国药准字H20070265",
        "category": "化学药品",
        "manufacturer": "杭州默沙东制药有限公司",
        "properties": "本品为薄膜衣片",
        "specification": "50mg*7片",
        "indications": "用于治疗原发性高血压",
        "adverse_reactions": "头晕、乏力",
        "usage_dosage": "口服。一日1次，一次1片",
        "status": "active"
    },
    {
        "title": "二甲双胍片",
        "generic_name": "二甲双胍",
        "trade_name": "格华止",
        "pinyin": "Er Jia Shuang Gu",
        "approval_number": "国药准字H20023370",
        "category": "化学药品",
        "manufacturer": "中美上海施贵宝制药有限公司",
        "properties": "本品为薄膜衣片",
        "specification": "0.5g*20片",
        "indications": "用于2型糖尿病",
        "adverse_reactions": "胃肠道反应",
        "usage_dosage": "口服。开始一次0.25g，一日2-3次",
        "status": "active"
    },
    {
        "title": "氨氯地平片",
        "generic_name": "氨氯地平",
        "trade_name": "络活喜",
        "pinyin": "An Lv Di Ping",
        "approval_number": "国药准字H20030317",
        "category": "化学药品",
        "manufacturer": "辉瑞制药有限公司",
        "properties": "本品为白色片",
        "specification": "5mg*7片",
        "indications": "用于高血压、心绞痛",
        "adverse_reactions": "头痛、水肿",
        "usage_dosage": "口服。一日1次，一次1片",
        "status": "active"
    },
    {
        "title": "奥美拉唑肠溶胶囊",
        "generic_name": "奥美拉唑",
        "trade_name": "洛赛克",
        "pinyin": "Ao Mei La Zuo",
        "approval_number": "国药准字H20033557",
        "category": "化学药品",
        "manufacturer": "阿斯利康制药有限公司",
        "properties": "本品为肠溶胶囊",
        "specification": "20mg*14粒",
        "indications": "用于胃溃疡、十二指肠溃疡",
        "adverse_reactions": "头痛、腹泻",
        "usage_dosage": "口服。一次1粒，一日1-2次",
        "status": "active"
    }
]

def import_medications():
    db = SessionLocal()
    try:
        print("开始导入示例药品数据...")
        
        for med_data in sample_medications:
            # 检查是否已存在
            exists = db.query(Medication).filter(
                Medication.generic_name == med_data["generic_name"],
                Medication.trade_name == med_data["trade_name"]
            ).first()
            
            if exists:
                print(f"  跳过已存在: {med_data['generic_name']} ({med_data['trade_name']})")
                continue
            
            medication = Medication(**med_data)
            db.add(medication)
            print(f"  添加药品: {med_data['generic_name']} ({med_data['trade_name']})")
        
        db.commit()
        
        count = db.query(Medication).count()
        print(f"\n✅ 导入完成！药品字典总数: {count}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 导入失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_medications()
