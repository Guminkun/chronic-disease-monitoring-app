from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from .. import schemas, dependencies, models
from ..database import get_db

router = APIRouter(
    prefix="/feedback",
    tags=["feedback"],
)

@router.post("/", response_model=schemas.FeedbackResponse, summary="提交意见反馈", description="用户提交意见反馈，支持文本和图片")
def create_feedback(
    feedback: schemas.FeedbackCreate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    提交意见反馈
    - content: 反馈内容（必填）
    - images: 图片URL列表（可选）
    - contact: 联系方式（可选）
    """
    db_feedback = models.Feedback(
        user_id=current_user.id,
        content=feedback.content,
        images=feedback.images,
        contact=feedback.contact,
        status=models.FeedbackStatus.pending
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    
    # 构建响应
    response = _build_feedback_response(db_feedback, db)
    return response

@router.get("/my", response_model=schemas.FeedbackListResponse, summary="获取我的反馈列表", description="获取当前用户提交的所有反馈")
def get_my_feedbacks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    获取当前用户的反馈列表
    """
    query = db.query(models.Feedback).filter(models.Feedback.user_id == current_user.id)
    total = query.count()
    
    items = query.order_by(models.Feedback.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()
    
    return schemas.FeedbackListResponse(
        items=[_build_feedback_response(item, db) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{feedback_id}", response_model=schemas.FeedbackResponse, summary="获取反馈详情", description="获取单条反馈的详细信息")
def get_feedback_detail(
    feedback_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    获取反馈详情
    - 普通用户只能查看自己的反馈
    - 管理员可以查看所有反馈
    """
    feedback = db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈不存在")
    
    # 权限检查：只有本人或管理员可以查看
    if feedback.user_id != current_user.id and current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="无权查看此反馈")
    
    return _build_feedback_response(feedback, db)

# ============ 管理端接口 ============

@router.get("/", response_model=schemas.FeedbackListResponse, summary="获取反馈列表(管理端)", description="管理员获取所有用户反馈列表")
def get_all_feedbacks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态筛选: pending/processing/replied/closed"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin)
):
    """
    管理员获取所有反馈列表
    - 支持状态筛选
    - 支持关键词搜索
    """
    query = db.query(models.Feedback)
    
    # 状态筛选
    if status:
        try:
            status_enum = models.FeedbackStatus(status)
            query = query.filter(models.Feedback.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的状态值")
    
    # 关键词搜索
    if keyword:
        query = query.filter(models.Feedback.content.ilike(f"%{keyword}%"))
    
    total = query.count()
    
    items = query.order_by(models.Feedback.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()
    
    return schemas.FeedbackListResponse(
        items=[_build_feedback_response(item, db) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )

@router.put("/{feedback_id}/status", response_model=schemas.FeedbackResponse, summary="更新反馈状态", description="管理员更新反馈处理状态")
def update_feedback_status(
    feedback_id: int,
    update_data: schemas.FeedbackUpdate,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin)
):
    """
    更新反馈状态
    """
    feedback = db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈不存在")
    
    if update_data.status:
        try:
            feedback.status = models.FeedbackStatus(update_data.status)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的状态值")
    
    db.commit()
    db.refresh(feedback)
    
    return _build_feedback_response(feedback, db)

@router.post("/{feedback_id}/reply", response_model=schemas.FeedbackResponse, summary="回复反馈", description="管理员回复用户反馈")
def reply_feedback(
    feedback_id: int,
    reply_data: schemas.FeedbackReply,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin)
):
    """
    管理员回复反馈
    - 回复后状态自动更新为"已回复"
    """
    feedback = db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈不存在")
    
    feedback.reply_content = reply_data.reply_content
    feedback.replied_at = datetime.now()
    feedback.replied_by = current_user.id
    feedback.status = models.FeedbackStatus.replied
    
    db.commit()
    db.refresh(feedback)
    
    return _build_feedback_response(feedback, db)

@router.delete("/{feedback_id}", summary="删除反馈", description="管理员删除反馈记录")
def delete_feedback(
    feedback_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_admin)
):
    """
    删除反馈
    """
    feedback = db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="反馈不存在")
    
    db.delete(feedback)
    db.commit()
    
    return {"message": "删除成功"}

# ============ 辅助函数 ============

def _build_feedback_response(feedback: models.Feedback, db: Session) -> schemas.FeedbackResponse:
    """构建反馈响应对象，包含用户信息"""
    # 获取用户信息
    user = db.query(models.User).filter(models.User.id == feedback.user_id).first()
    user_name = None
    user_phone = None
    
    if user:
        user_phone = user.phone
        if user.role == models.UserRole.patient:
            patient = db.query(models.Patient).filter(models.Patient.user_id == user.id).first()
            if patient:
                user_name = patient.name
        elif user.role == models.UserRole.doctor:
            doctor = db.query(models.Doctor).filter(models.Doctor.user_id == user.id).first()
            if doctor:
                user_name = doctor.name
    
    # 获取回复人信息
    replier_name = None
    if feedback.replied_by:
        replier = db.query(models.User).filter(models.User.id == feedback.replied_by).first()
        if replier:
            if replier.role == models.UserRole.admin:
                admin = db.query(models.Admin).filter(models.Admin.user_id == replier.id).first()
                if admin:
                    replier_name = admin.name
            elif replier.role == models.UserRole.doctor:
                doctor = db.query(models.Doctor).filter(models.Doctor.user_id == replier.id).first()
                if doctor:
                    replier_name = doctor.name
    
    return schemas.FeedbackResponse(
        id=feedback.id,
        user_id=feedback.user_id,
        content=feedback.content,
        images=feedback.images,
        contact=feedback.contact,
        status=feedback.status,
        reply_content=feedback.reply_content,
        replied_at=feedback.replied_at,
        replied_by=feedback.replied_by,
        created_at=feedback.created_at,
        updated_at=feedback.updated_at,
        user_name=user_name,
        user_phone=user_phone,
        replier_name=replier_name
    )
