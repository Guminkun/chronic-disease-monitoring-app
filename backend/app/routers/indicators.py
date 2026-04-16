from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/indicators",
    tags=["indicators"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.IndicatorResponse])
def get_indicators(
    q: Optional[str] = Query(None, description="搜索关键词（名称或分类）"),
    category: Optional[str] = Query(None, description="分类筛选"),
    db: Session = Depends(get_db)
):
    """
    获取指标列表，支持模糊搜索和分类筛选
    """
    query = db.query(models.Indicator)
    
    if category:
        query = query.filter(models.Indicator.category == category)
        
    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                models.Indicator.name.ilike(search),
                models.Indicator.category.ilike(search)
            )
        )
        
    return query.all()

@router.get("/categories", response_model=List[str])
def get_indicator_categories(db: Session = Depends(get_db)):
    """
    获取所有指标分类
    """
    # Distinct categories
    categories = db.query(models.Indicator.category).distinct().all()
    # categories is list of tuples [('Blood',), ('Urine',)]
    return [c[0] for c in categories if c[0]]
