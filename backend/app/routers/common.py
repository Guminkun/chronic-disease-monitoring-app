from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, dependencies

router = APIRouter(
    tags=["common"],
)

@router.get("/diseases", response_model=List[schemas.DiseaseResponse], summary="获取慢性病字典", description="获取系统支持的所有慢性病分类列表。")
def read_diseases(skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db)):
    """
    获取慢性病基础数据列表（分页）
    """
    return crud.get_diseases(db, skip=skip, limit=limit)
