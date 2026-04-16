from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from .config import settings

# JWT 密钥配置
# 实际生产环境中应该从环境变量获取
SECRET_KEY = settings.SECRET_KEY
# 加密算法
ALGORITHM = settings.ALGORITHM
# Token过期时间（分钟）
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# 密码哈希上下文，使用bcrypt算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """
    验证密码是否匹配
    :param plain_password: 明文密码
    :param hashed_password: 哈希后的密码
    :return: 布尔值，匹配返回True
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    获取密码的哈希值
    :param password: 明文密码
    :return: 哈希后的字符串
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    创建JWT访问令牌
    :param data: 包含在Token中的数据（载荷）
    :param expires_delta: 过期时间增量
    :return: 编码后的JWT字符串
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    # 添加过期时间到载荷
    to_encode.update({"exp": expire})
    
    # 生成JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
