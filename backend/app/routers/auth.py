from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import random
import httpx
from .. import crud, schemas, auth_utils, dependencies
from ..config import settings
from ..models import UserRole

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/register/patient", response_model=schemas.UserResponse, summary="患者注册", description="注册新患者账号，包含基本用户信息和患者档案。")
def register_patient(user: schemas.UserCreate, patient_info: schemas.PatientCreate, db: Session = Depends(dependencies.get_db)):
    """
    注册患者:
    - **user**: 用户基础信息（手机号、密码）
    - **patient_info**: 患者详细档案（姓名、性别、年龄等）
    """
    db_user = crud.get_user_by_phone(db, phone=user.phone)
    if db_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # 1. 创建基础用户账号
    new_user = crud.create_user(db=db, user=user)
    
    # 2. 创建患者详细档案
    crud.create_patient(db=db, patient=patient_info, user_id=new_user.id)
    
    return new_user

@router.post("/register/doctor", response_model=schemas.UserResponse, summary="医生注册", description="注册新医生账号，包含执业信息。")
def register_doctor(user: schemas.UserCreate, doctor_info: schemas.DoctorCreate, db: Session = Depends(dependencies.get_db)):
    """
    注册医生:
    - **user**: 用户基础信息
    - **doctor_info**: 医生执业信息（医院、科室、执照号等）
    """
    # 检查手机号是否已存在
    db_user = crud.get_user_by_phone(db, phone=user.phone)
    if db_user:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # 1. 创建基础用户账号
    new_user = crud.create_user(db=db, user=user)
    
    # 2. 创建医生详细档案
    crud.create_doctor(db=db, doctor=doctor_info, user_id=new_user.id)
    
    return new_user

@router.post("/token", response_model=schemas.Token, summary="用户登录", description="使用手机号和密码登录，获取访问令牌(Token)。")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(dependencies.get_db)):
    """
    获取Token:
    - **username**: 手机号
    - **password**: 密码
    """
    # 验证用户是否存在及密码是否正确
    user = crud.get_user_by_phone(db, phone=form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not auth_utils.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 设置Token过期时间
    access_token_expires = timedelta(minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 创建Access Token
    access_token = auth_utils.create_access_token(
        data={"sub": user.phone, "role": user.role.value, "user_id": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user.role.value, "user_id": user.id}

# In-memory storage for verification codes (phone -> code)
VERIFICATION_CODES = {}

@router.post("/sms/code", summary="发送验证码")
async def send_verification_code(request: schemas.SMSCodeRequest):
    """
    发送短信验证码
    """
    # Generate 6-digit code
    code = str(random.randint(100000, 999999))
    
    # Store code
    VERIFICATION_CODES[request.phone] = code
    
    # Send SMS via external service
    try:
        async with httpx.AsyncClient() as client:
            # Mocking the call or actual call if URL is real
            # payload = {"phone": request.phone, "code": code}
            # await client.post(settings.SMS_SERVICE_URL, json=payload)
            pass
    except Exception as e:
        # Log error but don't fail for now since it might be a mock URL
        print(f"Failed to send SMS: {e}")
    
    # For development convenience, return the code in response
    return {"message": "Verification code sent", "code": code}

@router.post("/sms/login", response_model=schemas.Token, summary="验证码登录")
def login_with_verification_code(request: schemas.SMSLoginRequest, db: Session = Depends(dependencies.get_db)):
    """
    使用验证码登录
    """
    # Verify code
    stored_code = VERIFICATION_CODES.get(request.phone)
    if not stored_code or stored_code != request.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )
    
    # Get user
    user = crud.get_user_by_phone(db, phone=request.phone)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Remove code after use
    VERIFICATION_CODES.pop(request.phone, None)
    
    # Create token
    access_token_expires = timedelta(minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_utils.create_access_token(
        data={"sub": user.phone, "role": user.role.value, "user_id": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "role": user.role.value, "user_id": user.id}

@router.post("/wechat/login", response_model=schemas.Token, summary="微信登录")
async def login_with_wechat(request: schemas.WeChatLoginRequest, db: Session = Depends(dependencies.get_db)):
    """
    使用微信登录
    - **code**: 微信小程序登录凭证
    """
    if not settings.WECHAT_APPID or not settings.WECHAT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="WeChat login not configured"
        )
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.weixin.qq.com/sns/jscode2session",
            params={
                "appid": settings.WECHAT_APPID,
                "secret": settings.WECHAT_SECRET,
                "js_code": request.code,
                "grant_type": "authorization_code"
            }
        )
    
    wechat_data = response.json()
    
    if "errcode" in wechat_data and wechat_data["errcode"] != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"WeChat login failed: {wechat_data.get('errmsg', 'Unknown error')}"
        )
    
    openid = wechat_data.get("openid")
    session_key = wechat_data.get("session_key")
    unionid = wechat_data.get("unionid")
    
    if not openid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get openid from WeChat"
        )
    
    user = crud.get_user_by_wechat_openid(db, openid=openid)
    
    if not user:
        user = crud.create_wechat_user(
            db=db,
            openid=openid,
            unionid=unionid,
            role=UserRole.patient
        )
        crud.create_patient(
            db=db,
            patient=schemas.PatientCreate(name="微信用户"),
            user_id=user.id
        )
    
    access_token_expires = timedelta(minutes=auth_utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_utils.create_access_token(
        data={"sub": openid, "role": user.role.value, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "role": user.role.value, "user_id": user.id}

@router.post("/wechat/update-profile", summary="更新微信用户信息")
async def update_wechat_profile(
    nickname: str = None,
    avatar: str = None,
    current_user = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    """
    更新微信用户的昵称和头像
    """
    if nickname:
        current_user.wechat_nickname = nickname
    if avatar:
        current_user.wechat_avatar = avatar
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "Profile updated successfully",
        "nickname": current_user.wechat_nickname,
        "avatar": current_user.wechat_avatar
    }
