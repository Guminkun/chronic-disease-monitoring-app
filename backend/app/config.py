from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """
    应用配置类
    从环境变量或.env文件中读取配置
    """
    # 数据库配置
    DATABASE_URL: str

    # 安全配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 后端地址（用于生成图片代理 URL）
    BACKEND_URL: str = "http://127.0.0.1:8000"
    
    # SMS Service
    SMS_SERVICE_URL: str = "http://mock-sms-service.com/send"
    
    # WeChat Mini Program Configuration
    WECHAT_APPID: str = ""
    WECHAT_SECRET: str = ""
    WECHAT_MEDICATION_TEMPLATE_ID: str = ""
    WECHAT_MONITORING_TEMPLATE_ID: str = ""

    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:8000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176"
    ]

    # Paddle OCR (异步 Job API)
    PADDLE_OCR_JOB_URL: str = "https://paddleocr.aistudio-app.com/api/v2/ocr/jobs"
    PADDLE_OCR_TOKEN: str
    PADDLE_OCR_MODEL: str = "PaddleOCR-VL"

    # MinIO
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str
    MINIO_BUCKET_REPORT: str | None = None
    MINIO_BUCKET_MEDICAL: str | None = None
    MINIO_BUCKET_AVATARS: str = "avatars"
    MINIO_BUCKET_GUIDES: str = "usageguides"
    MINIO_SECURE: bool = False

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    LOG_MAX_BYTES: int = 10 * 1024 * 1024
    LOG_BACKUP_COUNT: int = 5
    LOG_ENABLE_CONSOLE: bool = True
    LOG_ENABLE_FILE: bool = True

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
        env_file_encoding = "utf-8"
        case_sensitive = True

# 创建全局配置实例
settings = Settings()

# 启动时校验关键安全配置
_WEAK_SECRET_KEYS = {"your-secret-key-should-be-in-env-file", "secret", "change-me", ""}
if settings.SECRET_KEY in _WEAK_SECRET_KEYS:
    import warnings
    warnings.warn(
        "SECRET_KEY is using a weak or default value! "
        "Please set a strong SECRET_KEY in your .env file. "
        "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\"",
        stacklevel=2,
    )
