from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from PIL import Image
import io

from .. import models, dependencies
from ..database import get_db
from ..services.minio_service import minio_service
from ..config import settings

router = APIRouter(
    prefix="/upload",
    tags=["upload"],
)

@router.post("/avatar", response_model=dict, summary="上传头像")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    上传用户头像
    支持上传 jpg、png、gif、webp 格式图片
    自动压缩图片到 200x200 像素
    """
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
        
        file_key, md5_hash, _ = minio_service.upload_file(
            compressed_content, 
            str(current_user.id),
            "avatar",
            "avatars",
            "image/jpeg",
            bucket_name="avatars"
        )
        
        endpoint = settings.MINIO_ENDPOINT
        if not endpoint.startswith('http'):
            endpoint = f"http://{endpoint}"
        url = f"{endpoint}/avatars/{file_key}"
        
        return {"url": url, "filename": file_key}
    except Exception as e:
        print(f"头像上传失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"头像上传失败: {str(e)}")
