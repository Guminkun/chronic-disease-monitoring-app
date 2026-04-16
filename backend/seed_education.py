from app.database import SessionLocal, engine
from app import models
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_education():
    db = SessionLocal()
    try:
        # 创建表（如果不存在）
        models.Base.metadata.create_all(bind=engine)
        
        # 1. 种子分类
        categories_data = [
            {"name": "糖尿病", "sort_order": 10},
            {"name": "高血压", "sort_order": 9},
            {"name": "饮食指导", "sort_order": 8},
            {"name": "运动康复", "sort_order": 7},
            {"name": "心理健康", "sort_order": 6},
            {"name": "用药知识", "sort_order": 5},
        ]
        
        category_map = {} # name -> id
        
        logger.info("开始导入文章分类...")
        for data in categories_data:
            cat = db.query(models.ArticleCategory).filter(models.ArticleCategory.name == data["name"]).first()
            if not cat:
                cat = models.ArticleCategory(**data)
                db.add(cat)
                db.commit()
                db.refresh(cat)
                logger.info(f"添加分类: {data['name']}")
            category_map[data["name"]] = cat.id

        # 2. 种子文章
        articles_data = [
            {
                "title": "糖尿病患者饮食指南：科学控糖从餐桌开始",
                "category_id": category_map.get("糖尿病"),
                "author": "李医生",
                "summary": "详细解析糖尿病患者的饮食原则，推荐低GI食物，帮助您通过饮食控制血糖。",
                "content": """
                <h3>一、控制总热量</h3>
                <p>糖尿病患者应根据自身体重和活动量计算每日所需热量，合理分配。</p>
                <h3>二、合理搭配营养</h3>
                <p>建议碳水化合物占50%-60%，蛋白质占15%-20%，脂肪占25%-30%。</p>
                <h3>三、多吃高纤维食物</h3>
                <p>蔬菜、全谷物等富含膳食纤维，有助于延缓血糖上升。</p>
                """,
                "views": 13000,
                "duration": "8分钟",
                "is_recommended": True,
                "cover_image": "https://images.unsplash.com/photo-1505576399279-565b52d4ac71?auto=format&fit=crop&q=80&w=800"
            },
            {
                "title": "高血压患者居家监测指南",
                "category_id": category_map.get("高血压"),
                "author": "王主任",
                "summary": "教您如何正确使用血压计，记录血压数据，以及何时需要就医。",
                "content": "<p>定期测量血压是控制高血压的关键...</p>",
                "views": 9870,
                "duration": "6分钟",
                "is_recommended": True,
                "cover_image": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&q=80&w=800"
            },
            {
                "title": "慢性病患者的运动处方：安全有效的锻炼方法",
                "category_id": category_map.get("运动康复"),
                "author": "张教授",
                "summary": "针对不同慢性病人群的运动建议，包括运动强度、频率和注意事项。",
                "content": "<p>运动是良医，但需要科学进行...</p>",
                "views": 7650,
                "duration": "12分钟",
                "is_recommended": True,
                "cover_image": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?auto=format&fit=crop&q=80&w=800"
            },
            {
                "title": "如何正确服用降压药物",
                "category_id": category_map.get("用药知识"),
                "author": "陈药师",
                "summary": "降压药什么时候吃最好？漏服了怎么办？药师为您解答常见用药问题。",
                "content": "<p>坚持规律服药是血压达标的基础...</p>",
                "views": 15000,
                "duration": "5分钟",
                "is_recommended": False,
                "cover_image": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&q=80&w=800"
            },
             {
                "title": "慢性病患者的心理调适",
                "category_id": category_map.get("心理健康"),
                "author": "刘心理师",
                "summary": "面对慢性病，如何保持积极乐观的心态，缓解焦虑和抑郁情绪。",
                "content": "<p>身心健康同等重要...</p>",
                "views": 5480,
                "duration": "10分钟",
                "is_recommended": False,
                "cover_image": "https://images.unsplash.com/photo-1493836512294-502baa1986e2?auto=format&fit=crop&q=80&w=800"
            },
             {
                "title": "控制血糖的10种超级食物",
                "category_id": category_map.get("饮食指导"),
                "author": "营养师团队",
                "summary": "盘点10种对血糖友好的食物，建议加入您的日常食谱。",
                "content": "<p>燕麦、苦瓜、洋葱...</p>",
                "views": 19000,
                "duration": "7分钟",
                "is_recommended": False,
                "cover_image": "https://images.unsplash.com/photo-1490645935967-10de6ba17061?auto=format&fit=crop&q=80&w=800"
            }
        ]

        logger.info("开始导入文章数据...")
        count = 0
        for data in articles_data:
            exists = db.query(models.Article).filter(models.Article.title == data["title"]).first()
            if not exists:
                article = models.Article(**data)
                db.add(article)
                count += 1
                logger.info(f"添加文章: {data['title']}")
            else:
                logger.info(f"文章已存在: {data['title']}")
        
        db.commit()
        logger.info(f"导入完成，共添加 {count} 篇文章")

    except Exception as e:
        logger.error(f"导入出错: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_education()
