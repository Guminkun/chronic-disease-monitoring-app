from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from . import crud, models, schemas, database, auth_utils

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth_utils.SECRET_KEY, algorithms=[auth_utils.ALGORITHM])
        sub: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if sub is None:
            raise credentials_exception
        
        token_data = schemas.TokenData(phone=sub, user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    # 优先通过 user_id 查找用户
    if token_data.user_id:
        user = db.query(models.User).filter(models.User.id == token_data.user_id).first()
    else:
        # 兼容旧的token，通过 phone 查找
        user = crud.get_user_by_phone(db, phone=token_data.phone)
    
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin(current_user: models.User = Depends(get_current_user)):
    """获取当前管理员用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user
