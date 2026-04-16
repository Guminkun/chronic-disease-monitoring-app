from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, models, dependencies
from ..services.minio_service import minio_service
from uuid import UUID
from PIL import Image
import io

router = APIRouter(
    prefix="/members",
    tags=["members"],
)

@router.get("/", response_model=List[schemas.MemberResponse], summary="获取成员列表")
def get_members(
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    """
    获取当前患者的所有成员列表
    如果没有成员，自动创建"自己"成员并设为当前成员
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="仅患者可访问")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者档案不存在")
    
    members = db.query(models.Member).filter(
        models.Member.patient_id == patient.id
    ).order_by(models.Member.created_at).all()
    
    if not members:
        default_nickname = patient.name if patient.name else "自己"
        default_member = models.Member(
            patient_id=patient.id,
            nickname=default_nickname,
            relation="自己",
            is_current=True
        )
        db.add(default_member)
        db.commit()
        db.refresh(default_member)
        members = [default_member]
    
    return members

@router.post("/", response_model=schemas.MemberResponse, summary="创建成员")
def create_member(
    member_data: schemas.MemberCreate,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    """
    创建新成员
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="仅患者可访问")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者档案不存在")
    
    new_member = models.Member(
        patient_id=patient.id,
        nickname=member_data.nickname,
        relation=member_data.relation,
        avatar_url=member_data.avatar_url,
        age=member_data.age,
        gender=member_data.gender,
        height=member_data.height,
        weight=member_data.weight,
        blood_type=member_data.blood_type,
        lifestyle=member_data.lifestyle,
        allergy_history=member_data.allergy_history,
        past_history=member_data.past_history,
        family_history=member_data.family_history,
        surgery_history=member_data.surgery_history,
        other_notes=member_data.other_notes,
        is_current=False
    )
    
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    
    return new_member

@router.get("/{member_id}", response_model=schemas.MemberResponse, summary="获取成员详情")
def get_member(
    member_id: UUID,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    """
    获取指定成员的详细信息
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="仅患者可访问")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者档案不存在")
    
    member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.patient_id == patient.id
    ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="成员不存在")
    
    return member

@router.put("/{member_id}", response_model=schemas.MemberResponse, summary="更新成员信息")
def update_member(
    member_id: UUID,
    member_data: schemas.MemberUpdate,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    """
    更新成员信息
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="仅患者可访问")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者档案不存在")
    
    member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.patient_id == patient.id
    ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="成员不存在")
    
    update_data = member_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(member, field, value)
    
    db.commit()
    db.refresh(member)
    
    return member

@router.delete("/{member_id}", summary="删除成员")
def delete_member(
    member_id: UUID,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    """
    删除成员及其所有相关数据
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="仅患者可访问")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者档案不存在")
    
    member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.patient_id == patient.id
    ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="成员不存在")
    
    if member.is_current:
        raise HTTPException(status_code=400, detail="不能删除当前操作的成员")
    
    db.delete(member)
    db.commit()
    
    return {"message": "删除成功"}

@router.post("/{member_id}/set-current", summary="设置当前成员")
def set_current_member(
    member_id: UUID,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    """
    设置指定成员为当前操作成员
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="仅患者可访问")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者档案不存在")
    
    member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.patient_id == patient.id
    ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="成员不存在")
    
    db.query(models.Member).filter(
        models.Member.patient_id == patient.id
    ).update({"is_current": False})
    
    member.is_current = True
    db.commit()
    
    return {"message": "切换成功"}

@router.get("/current", response_model=schemas.MemberResponse, summary="获取当前成员")
def get_current_member(
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    """
    获取当前操作的成员
    如果没有成员，自动创建"自己"成员
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="仅患者可访问")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="患者档案不存在")
    
    current_member = db.query(models.Member).filter(
        models.Member.patient_id == patient.id,
        models.Member.is_current == True
    ).first()
    
    if not current_member:
        members = db.query(models.Member).filter(
            models.Member.patient_id == patient.id
        ).order_by(models.Member.created_at).all()
        
        if members:
            members[0].is_current = True
            db.commit()
            db.refresh(members[0])
            return members[0]
        else:
            default_nickname = patient.name if patient.name else "自己"
            default_member = models.Member(
                patient_id=patient.id,
                nickname=default_nickname,
                relation="自己",
                is_current=True
            )
            db.add(default_member)
            db.commit()
            db.refresh(default_member)
            return default_member
    
    return current_member

@router.post("/upload-avatar", response_model=dict, summary="上传成员头像")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    """
    上传成员头像
    支持上传 jpg、png、gif、webp 格式图片
    自动压缩图片到 200x200 像素
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="仅患者可访问")
    
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的图片格式，仅支持: {', '.join(allowed_types)}"
        )
    
    try:
        file_content = await file.read()
        
        image = Image.open(io.BytesIO(file_content))
        
        max_size = (200, 200)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        output_buffer = io.BytesIO()
        image.save(output_buffer, format='JPEG', quality=85)
        compressed_content = output_buffer.getvalue()
        
        url, object_name = minio_service.upload_file(
            file_data=compressed_content,
            filename=f"avatar_{current_user.id}.jpg",
            content_type="image/jpeg",
            bucket_name="avatars"
        )
        
        return {"url": url, "filename": object_name}
    except Exception as e:
        print(f"头像上传失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"头像上传失败: {str(e)}")
