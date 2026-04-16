from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from .. import schemas, models
from ..dependencies import get_db

router = APIRouter(
    prefix="/report-types",
    tags=["report-types"],
)

@router.get("/", response_model=List[schemas.ReportTypeResponse])
def get_report_types(
    q: Optional[str] = Query(None, description="搜索关键词（名称或大类）"),
    category: Optional[str] = Query(None, description="大类筛选"),
    db: Session = Depends(get_db)
):
    """
    获取报告类型列表，支持模糊搜索和分类筛选
    """
    query = db.query(models.ReportType)
    
    if category:
        query = query.filter(models.ReportType.category == category)
        
    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                models.ReportType.name.ilike(search),
                models.ReportType.category.ilike(search)
            )
        )
        
    return query.all()

@router.get("/categories", response_model=List[str])
def get_report_type_categories(db: Session = Depends(get_db)):
    """
    获取所有报告大类
    """
    # Distinct categories
    categories = db.query(models.ReportType.category).distinct().all()
    return [c[0] for c in categories if c[0]]
