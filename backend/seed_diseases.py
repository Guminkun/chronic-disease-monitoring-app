from app.database import SessionLocal, engine
from app import models
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_diseases():
    db = SessionLocal()
    try:
        # 创建表（如果不存在）
        models.Base.metadata.create_all(bind=engine)
        
        # 初始数据
        diseases_data = [
            {"name": "高血压", "category": "心血管疾病", "description": "一种以体循环动脉血压（收缩压和/或舒张压）增高为主要特征的临床综合征"},
            {"name": "2型糖尿病", "category": "内分泌代谢疾病", "description": "以高血糖为特征的代谢性疾病"},
            {"name": "冠心病", "category": "心血管疾病", "description": "冠状动脉血管发生动脉粥样硬化病变而引起血管腔狭窄或阻塞，造成心肌缺血、缺氧或坏死而导致的心脏病"},
            {"name": "慢性阻塞性肺疾病", "category": "呼吸系统疾病", "description": "一种具有气流阻塞特征的慢性支气管炎和（或）肺气肿"},
            {"name": "脑卒中", "category": "脑血管疾病", "description": "又称中风、脑血管意外"},
            {"name": "哮喘", "category": "呼吸系统疾病", "description": "由多种细胞和细胞组分参与的气道慢性炎症性疾病"},
            {"name": "慢性肾脏病", "category": "泌尿系统疾病", "description": "各种原因引起的慢性肾脏结构和功能障碍"},
            {"name": "高脂血症", "category": "内分泌代谢疾病", "description": "脂肪代谢或运转异常使血浆一种或多种脂质高于正常"},
            {"name": "骨质疏松", "category": "骨骼肌肉系统疾病", "description": "以骨量低，骨组织微结构损坏，导致骨脆性增加，易发生骨折为特征的全身性骨病"},
            {"name": "阿尔茨海默病", "category": "神经系统疾病", "description": "一种起病隐匿的进行性发展的神经系统退行性疾病"}
        ]
        
        logger.info("开始导入疾病数据...")
        count = 0
        for data in diseases_data:
            exists = db.query(models.Disease).filter(models.Disease.name == data["name"]).first()
            if not exists:
                disease = models.Disease(**data)
                db.add(disease)
                count += 1
                logger.info(f"添加疾病: {data['name']}")
            else:
                logger.info(f"疾病已存在: {data['name']}")
        
        db.commit()
        logger.info(f"导入完成，共添加 {count} 条记录")
        
    except Exception as e:
        logger.error(f"导入出错: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_diseases()
