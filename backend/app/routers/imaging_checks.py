from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from .. import schemas, models
from ..dependencies import get_db

router = APIRouter(
    prefix="/imaging-checks",
    tags=["imaging-checks"],
)

@router.get("/", response_model=List[schemas.ImagingCheckResponse])
def get_imaging_checks(
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    part: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    enhanced: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(models.HospitalImagingCheck)

    if category:
        query = query.filter(models.HospitalImagingCheck.check_category == category)
    if part:
        query = query.filter(models.HospitalImagingCheck.check_part == part)
    if gender:
        query = query.filter(
            or_(
                models.HospitalImagingCheck.applicable_gender == "通用",
                models.HospitalImagingCheck.applicable_gender == gender
            )
        )
    if enhanced is not None:
        query = query.filter(models.HospitalImagingCheck.is_enhanced == enhanced)
    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                models.HospitalImagingCheck.check_subcategory.ilike(search),
                models.HospitalImagingCheck.check_part.ilike(search),
                models.HospitalImagingCheck.check_category.ilike(search),
                models.HospitalImagingCheck.department.ilike(search)
            )
        )

    return query.order_by(
        models.HospitalImagingCheck.check_category.asc(),
        models.HospitalImagingCheck.sort_num.asc(),
        models.HospitalImagingCheck.check_id.asc()
    ).limit(limit).all()

@router.get("/categories", response_model=List[str])
def get_imaging_check_categories(db: Session = Depends(get_db)):
    rows = db.query(models.HospitalImagingCheck.check_category).distinct().all()
    return [r[0] for r in rows if r and r[0]]

@router.get("/{check_id}", response_model=schemas.ImagingCheckResponse)
def get_imaging_check(check_id: str, db: Session = Depends(get_db)):
    item = db.query(models.HospitalImagingCheck).filter(models.HospitalImagingCheck.check_id == check_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Imaging check not found")
    return item
