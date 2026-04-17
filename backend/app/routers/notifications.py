from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta
from .. import models, schemas, dependencies, crud
from ..database import get_db
from ..services.notification_service import notification_service
from pydantic import UUID4

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)

@router.get("/", response_model=schemas.NotificationListResponse, summary="获取通知列表")
def get_notifications(
    member_id: Optional[UUID4] = None,
    is_read: Optional[bool] = None,
    is_handled: Optional[bool] = Query(None, description="是否已处理"),
    category: Optional[str] = None,
    type: Optional[str] = None,
    all_members: bool = Query(False, description="是否获取所有成员的通知"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取通知列表
    - 支持按成员筛选
    - 支持按已读/未读筛选
    - 支持按已处理/未处理筛选
    - 支持按分类筛选
    - 支持按类型筛选
    - all_members=true 时获取所有成员的通知
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="仅患者可访问")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者档案不存在")
    
    # 自动生成提醒通知并保存到数据库
    notification_service.generate_all_reminders(db, patient.id)
    
    query = db.query(models.Notification).filter(
        models.Notification.patient_id == patient.id
    )
    
    if not all_members:
        target_member_id = member_id
        if not target_member_id:
            current_member = db.query(models.Member).filter(
                models.Member.patient_id == patient.id,
                models.Member.is_current == True
            ).first()
            if current_member:
                target_member_id = current_member.id
        
        if target_member_id:
            query = query.filter(models.Notification.member_id == target_member_id)
    
    if is_read is not None:
        query = query.filter(models.Notification.is_read == is_read)
    
    if is_handled is not None:
        query = query.filter(models.Notification.is_handled == is_handled)
    
    if category:
        query = query.filter(models.Notification.category == category)
    
    if type:
        query = query.filter(models.Notification.type == type)
    
    total = query.count()
    unread_count = db.query(models.Notification).filter(
        models.Notification.patient_id == patient.id,
        models.Notification.is_read == False,
        models.Notification.is_handled == False
    ).count()
    
    unhandled_count = db.query(models.Notification).filter(
        models.Notification.patient_id == patient.id,
        models.Notification.is_handled == False
    ).count()
    
    items = query.order_by(
        models.Notification.is_read.asc(),
        models.Notification.priority.desc(),
        models.Notification.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    items_with_member = []
    for item in items:
        member_nickname = None
        member_relation = None
        if item.member:
            member_nickname = item.member.nickname
            member_relation = item.member.relation
        items_with_member.append(schemas.NotificationResponse(
            id=item.id,
            patient_id=item.patient_id,
            member_id=item.member_id,
            title=item.title,
            content=item.content,
            type=item.type,
            category=item.category,
            source_id=item.source_id,
            source_type=item.source_type,
            priority=item.priority,
            extra_data=item.extra_data,
            is_read=item.is_read,
            read_at=item.read_at,
            is_handled=item.is_handled,
            handled_at=item.handled_at,
            handler_type=item.handler_type,
            created_at=item.created_at,
            member_nickname=member_nickname,
            member_relation=member_relation
        ))
    
    return {
        "items": items_with_member,
        "total": total,
        "unread_count": unread_count,
        "unhandled_count": unhandled_count
    }

@router.post("/", response_model=schemas.NotificationResponse, summary="创建通知")
def create_notification(
    notification: schemas.NotificationCreate,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建新通知（系统内部使用）
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="仅患者可访问")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者档案不存在")
    
    target_member_id = notification.member_id
    if not target_member_id:
        current_member = db.query(models.Member).filter(
            models.Member.patient_id == patient.id,
            models.Member.is_current == True
        ).first()
        if current_member:
            target_member_id = current_member.id
    
    db_notification = models.Notification(
        patient_id=patient.id,
        member_id=target_member_id,
        title=notification.title,
        content=notification.content,
        type=notification.type,
        category=notification.category,
        source_id=notification.source_id,
        source_type=notification.source_type,
        priority=notification.priority or 0,
        extra_data=notification.extra_data
    )
    
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    
    return db_notification

@router.put("/{notification_id}/read", summary="标记通知为已读")
def mark_as_read(
    notification_id: int,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    标记单条通知为已读
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="仅患者可访问")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者档案不存在")
    
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.patient_id == patient.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.commit()
    
    return {"message": "已标记为已读"}

@router.put("/read-all", summary="标记所有通知为已读")
def mark_all_as_read(
    member_id: Optional[UUID4] = None,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    标记所有通知为已读
    - 可指定成员，不指定则标记当前成员
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="仅患者可访问")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者档案不存在")
    
    target_member_id = member_id
    if not target_member_id:
        current_member = db.query(models.Member).filter(
            models.Member.patient_id == patient.id,
            models.Member.is_current == True
        ).first()
        if current_member:
            target_member_id = current_member.id
    
    query = db.query(models.Notification).filter(
        models.Notification.patient_id == patient.id,
        models.Notification.is_read == False
    )
    
    if target_member_id:
        query = query.filter(models.Notification.member_id == target_member_id)
    
    query.update({
        models.Notification.is_read: True,
        models.Notification.read_at: datetime.utcnow()
    })
    
    db.commit()
    
    return {"message": "所有通知已标记为已读"}

@router.delete("/{notification_id}", summary="删除通知")
def delete_notification(
    notification_id: int,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除单条通知
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="仅患者可访问")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者档案不存在")
    
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.patient_id == patient.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")
    
    db.delete(notification)
    db.commit()
    
    return {"message": "删除成功"}

@router.get("/unread-count", summary="获取未读通知数量")
def get_unread_count(
    member_id: Optional[UUID4] = None,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取未读通知数量
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="仅患者可访问")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者档案不存在")
    
    target_member_id = member_id
    if not target_member_id:
        current_member = db.query(models.Member).filter(
            models.Member.patient_id == patient.id,
            models.Member.is_current == True
        ).first()
        if current_member:
            target_member_id = current_member.id
    
    query = db.query(models.Notification).filter(
        models.Notification.patient_id == patient.id,
        models.Notification.is_read == False
    )
    
    if target_member_id:
        query = query.filter(models.Notification.member_id == target_member_id)
    
    count = query.count()
    
    return {"unread_count": count}

@router.put("/{notification_id}/handle", summary="标记通知为已处理")
def mark_notification_as_handled(
    notification_id: int,
    handler_type: str = Query("user", description="处理方式: user 或 auto"),
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    标记单条通知为已处理
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="仅患者可访问")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者档案不存在")
    
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.patient_id == patient.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")
    
    notification.is_handled = True
    notification.handled_at = datetime.utcnow()
    notification.handler_type = handler_type
    
    db.commit()
    db.refresh(notification)
    
    return {
        "message": "已标记为处理",
        "id": notification.id,
        "is_handled": notification.is_handled,
        "handled_at": notification.handled_at
    }

@router.put("/handle-all", summary="批量标记已处理")
def mark_all_notifications_as_handled(
    member_id: Optional[UUID4] = None,
    type: Optional[str] = None,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    批量标记通知为已处理
    - 可按成员筛选
    - 可按类型筛选
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="仅患者可访问")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者档案不存在")
    
    query = db.query(models.Notification).filter(
        models.Notification.patient_id == patient.id,
        models.Notification.is_handled == False
    )
    
    if member_id:
        query = query.filter(models.Notification.member_id == member_id)
    
    if type:
        query = query.filter(models.Notification.type == type)
    
    count = query.count()
    
    query.update({
        models.Notification.is_handled: True,
        models.Notification.handled_at: datetime.utcnow(),
        models.Notification.handler_type: "user"
    }, synchronize_session=False)
    
    db.commit()
    
    return {
        "message": f"已标记 {count} 条通知为已处理",
        "handled_count": count
    }
