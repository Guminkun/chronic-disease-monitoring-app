"""
使用说明 API 路由
提供使用说明的 CRUD 接口和文件上传功能
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import json

from .. import models, schemas
from ..database import get_db
from ..services.minio_service import minio_service

router = APIRouter(
    prefix="/usage-guides",
    tags=["usage-guides"]
)


@router.get("/", response_model=schemas.UsageGuideListResponse)
def get_usage_guides(
    q: Optional[str] = Query(None, description="搜索关键词（标题、描述）"),
    is_published: Optional[bool] = Query(None, description="发布状态筛选"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    获取使用说明列表（管理端）
    支持搜索、发布状态筛选
    """
    query = db.query(models.UsageGuide)
    
    # 搜索过滤
    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                models.UsageGuide.title.ilike(search),
                models.UsageGuide.description.ilike(search)
            )
        )
    
    # 发布状态过滤
    if is_published is not None:
        query = query.filter(models.UsageGuide.is_published == is_published)
    
    # 统计总数
    total = query.count()
    
    # 排序并分页
    query = query.order_by(models.UsageGuide.sort_order.desc(), models.UsageGuide.created_at.desc())
    items = query.offset(skip).limit(limit).all()
    
    return {
        "items": items,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }


@router.get("/published", response_model=List[schemas.UsageGuideResponse])
def get_published_usage_guides(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    获取已发布的使用说明列表（移动端）
    仅返回 is_published=True 的数据
    """
    query = db.query(models.UsageGuide).filter(models.UsageGuide.is_published == True)
    
    # 排序并分页
    query = query.order_by(models.UsageGuide.sort_order.desc(), models.UsageGuide.created_at.desc())
    return query.offset(skip).limit(limit).all()


@router.get("/{guide_id}", response_model=schemas.UsageGuideResponse)
def get_usage_guide(
    guide_id: int,
    db: Session = Depends(get_db)
):
    """
    获取使用说明详情
    """
    guide = db.query(models.UsageGuide).filter(models.UsageGuide.id == guide_id).first()
    if not guide:
        raise HTTPException(status_code=404, detail="使用说明不存在")
    
    # 增加浏览量
    guide.views = (guide.views or 0) + 1
    db.commit()
    
    return guide


@router.post("/", response_model=schemas.UsageGuideResponse, status_code=status.HTTP_201_CREATED)
def create_usage_guide(
    guide: schemas.UsageGuideCreate,
    db: Session = Depends(get_db)
):
    """
    创建使用说明（管理端）
    """
    db_guide = models.UsageGuide(**guide.dict())
    db.add(db_guide)
    db.commit()
    db.refresh(db_guide)
    return db_guide


@router.put("/{guide_id}", response_model=schemas.UsageGuideResponse)
def update_usage_guide(
    guide_id: int,
    guide_update: schemas.UsageGuideUpdate,
    db: Session = Depends(get_db)
):
    """
    更新使用说明（管理端）
    """
    db_guide = db.query(models.UsageGuide).filter(models.UsageGuide.id == guide_id).first()
    if not db_guide:
        raise HTTPException(status_code=404, detail="使用说明不存在")
    
    update_data = guide_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_guide, key, value)
    
    db.commit()
    db.refresh(db_guide)
    return db_guide


@router.delete("/{guide_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usage_guide(
    guide_id: int,
    db: Session = Depends(get_db)
):
    """
    删除使用说明（管理端）
    """
    db_guide = db.query(models.UsageGuide).filter(models.UsageGuide.id == guide_id).first()
    if not db_guide:
        raise HTTPException(status_code=404, detail="使用说明不存在")
    
    db.delete(db_guide)
    db.commit()
    return None


@router.post("/upload/image", response_model=dict)
async def upload_image(
    file: UploadFile = File(...),
):
    """
    上传使用说明图片（管理端）
    支持上传 jpg、png、gif、webp 格式图片
    """
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的图片格式，仅支持: {', '.join(allowed_types)}"
        )
    
    # 读取文件内容
    file_content = await file.read()
    
    try:
        file_key, md5_hash, _ = minio_service.upload_file(
            file_content, 
            "system",
            "guides",
            "usageguides",
            file.content_type or "image/jpeg",
            bucket_name="usageguides"
        )
        url = minio_service.get_presigned_url(file_key, bucket_name="usageguides")
        return {"url": url, "filename": file_key}
    except Exception as e:
        print(f"图片上传失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"图片上传失败: {str(e)}")


@router.post("/upload/video", response_model=dict)
async def upload_video(
    file: UploadFile = File(...),
):
    """
    上传使用说明视频（管理端）
    支持上传 mp4、webm、mov 格式视频
    """
    # 验证文件类型
    allowed_types = ["video/mp4", "video/webm", "video/quicktime"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的视频格式，仅支持: {', '.join(allowed_types)}"
        )
    
    # 读取文件内容
    file_content = await file.read()
    
    try:
        file_key, md5_hash, _ = minio_service.upload_file(
            file_content, 
            "system",
            "guides",
            "usageguides",
            file.content_type or "video/mp4",
            bucket_name="usageguides",
            compress=False
        )
        url = minio_service.get_presigned_url(file_key, bucket_name="usageguides")
        return {"url": url, "filename": file_key}
    except Exception as e:
        print(f"视频上传失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"视频上传失败: {str(e)}")


@router.post("/batch-delete", status_code=status.HTTP_204_NO_CONTENT)
def batch_delete_usage_guides(
    request: schemas.BatchDeleteRequest,
    db: Session = Depends(get_db)
):
    """
    批量删除使用说明（管理端）
    """
    db.query(models.UsageGuide).filter(models.UsageGuide.id.in_(request.ids)).delete(synchronize_session=False)
    db.commit()
    return None


@router.put("/{guide_id}/publish", response_model=schemas.UsageGuideResponse)
def toggle_publish(
    guide_id: int,
    db: Session = Depends(get_db)
):
    """
    切换发布状态（管理端）
    """
    db_guide = db.query(models.UsageGuide).filter(models.UsageGuide.id == guide_id).first()
    if not db_guide:
        raise HTTPException(status_code=404, detail="使用说明不存在")
    
    db_guide.is_published = not db_guide.is_published
    db.commit()
    db.refresh(db_guide)
    return db_guide
