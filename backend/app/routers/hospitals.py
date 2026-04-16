from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/hospitals",
    tags=["hospitals"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.HospitalResponse])
def get_hospitals(
    q: Optional[str] = Query(None, description="搜索关键词（名称、别名或城市）"),
    city: Optional[str] = Query(None, description="城市筛选"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Hospital)
    
    if city:
        query = query.filter(models.Hospital.city == city)
        
    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                models.Hospital.name.ilike(search),
                models.Hospital.alias.ilike(search),
                models.Hospital.city.ilike(search)
            )
        )
    
    # Limit results to avoid overwhelming response if no filter
    if not q and not city:
        return query.limit(50).all()
        
    return query.all()

@router.get("/{hospital_id}", response_model=schemas.HospitalResponse)
def get_hospital(hospital_id: int, db: Session = Depends(get_db)):
    hospital = db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()
    if hospital is None:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital
