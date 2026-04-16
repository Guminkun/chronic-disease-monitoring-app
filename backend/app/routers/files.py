from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.minio_service import minio_service
from app import models, dependencies, crud
from app.logging_config import get_logger
from pydantic import UUID4
from typing import Optional

logger = get_logger(__name__)

router = APIRouter(
    prefix="/files",
    tags=["files"]
)


@router.get("/presigned-url")
def get_presigned_url(
    file_key: str = Query(..., description="File key path"),
    bucket_name: Optional[str] = Query(None, description="Bucket name"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    Get a presigned URL for file access.
    
    Security:
    - Validates that the file belongs to the current user
    - Returns a temporary URL valid for 10 minutes
    """
    try:
        # Security check: validate file ownership
        # Extract user_id and member_id from file_key
        # Format: user_{user_id}/member_{member_id}/{file_type}/{filename}
        if not file_key.startswith("user_"):
            raise HTTPException(status_code=403, detail="Invalid file key format")
        
        # Extract user_id from key
        parts = file_key.split("/")
        if len(parts) < 2:
            raise HTTPException(status_code=403, detail="Invalid file key format")
        
        key_user_id = parts[0].replace("user_", "")
        
        # Validate ownership
        if current_user.role == models.UserRole.patient:
            patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
            if not patient:
                raise HTTPException(status_code=404, detail="Patient profile not found")
            
            if str(current_user.id) != key_user_id:
                logger.warning(f"User {current_user.id} attempted to access file owned by user {key_user_id}")
                raise HTTPException(status_code=403, detail="You do not have permission to access this file")
        
        # Generate presigned URL
        url = minio_service.get_presigned_url(file_key, bucket_name)
        
        logger.info(f"Generated presigned URL for user {current_user.id}: {file_key}")
        
        return {
            "success": True,
            "url": url,
            "expires_in": 600  # 10 minutes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate file access URL")


@router.get("/report/{report_id}/image")
def get_report_image_url(
    report_id: UUID4,
    thumbnail: bool = Query(False, description="Get thumbnail instead of full image"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    Get presigned URL for report image.
    Validates that the user owns the report.
    """
    report = crud.get_report(db, report_id=report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check permission
    if current_user.role == models.UserRole.patient:
        patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
        if not patient or report.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this report")
    
    # Get file key from report
    if not report.image_url:
        raise HTTPException(status_code=404, detail="Report has no image")
    
    # Use thumbnail if requested and available
    file_key = report.image_url
    if thumbnail and report.thumbnail_url:
        file_key = report.thumbnail_url
    
    try:
        url = minio_service.get_presigned_url(file_key)
        return {
            "success": True,
            "url": url,
            "expires_in": 600
        }
    except Exception as e:
        logger.error(f"Failed to generate presigned URL for report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate image URL")


@router.get("/member/{member_id}/avatar")
def get_member_avatar_url(
    member_id: UUID4,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    Get presigned URL for member avatar.
    Validates that the user owns the member.
    """
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Check permission
    if current_user.role == models.UserRole.patient:
        patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
        if not patient or member.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this member")
    
    if not member.avatar_url:
        raise HTTPException(status_code=404, detail="Member has no avatar")
    
    try:
        url = minio_service.get_presigned_url(member.avatar_url, bucket_name="avatars")
        return {
            "success": True,
            "url": url,
            "expires_in": 600
        }
    except Exception as e:
        logger.error(f"Failed to generate avatar URL for member {member_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate avatar URL")


@router.delete("/cleanup/member/{member_id}")
def cleanup_member_files(
    member_id: UUID4,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    Delete all files for a member (for cascade deletion).
    Only called internally when deleting a member.
    """
    # Check permission
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Only admins can call this endpoint")
    
    member = db.query(models.Member).filter(models.Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    try:
        # Delete all files for this member
        # Format: user_{user_id}/member_{member_id}/
        patient = db.query(models.Patient).filter(models.Patient.id == member.patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        prefix = f"user_{patient.user_id}/member_{member_id}/"
        
        # Delete from all buckets
        buckets = ["jianchabaogao", "binli", "avatars", "usageguides"]
        total_deleted = 0
        
        for bucket in buckets:
            deleted = minio_service.delete_files_by_prefix(prefix, bucket_name=bucket)
            total_deleted += deleted
        
        logger.info(f"Deleted {total_deleted} files for member {member_id}")
        
        return {
            "success": True,
            "files_deleted": total_deleted
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup files for member {member_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup member files")
