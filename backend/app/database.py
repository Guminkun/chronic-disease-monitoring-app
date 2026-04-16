from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# 数据库连接URL
# 格式: postgresql://用户:密码@主机/数据库名
# 生产环境建议从环境变量读取
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 创建数据库引擎
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明式基类，所有模型继承此类
Base = declarative_base()

def get_db():
    """
    获取数据库会话(Session)依赖
    用于FastAPI的Depends注入
    确保每次请求后关闭会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
