from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from typing import List, Optional
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/education",
    tags=["education"]
)

# --- Categories ---

@router.get("/categories", response_model=List[schemas.ArticleCategoryResponse])
def get_categories(
    db: Session = Depends(get_db)
):
    """
    获取文章分类列表
    """
    return db.query(models.ArticleCategory)\
        .filter(models.ArticleCategory.is_active == True)\
        .order_by(models.ArticleCategory.sort_order.desc())\
        .all()

@router.post("/categories", response_model=schemas.ArticleCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: schemas.ArticleCategoryCreate,
    db: Session = Depends(get_db)
):
    """
    (管理端) 创建分类
    """
    db_category = models.ArticleCategory(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

# --- Articles ---

@router.get("/articles", response_model=List[schemas.ArticleResponse])
def get_articles(
    category_id: Optional[int] = Query(None, description="分类ID"),
    q: Optional[str] = Query(None, description="搜索关键词"),
    is_recommended: Optional[bool] = Query(None, description="是否推荐"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取文章列表，支持搜索、筛选
    """
    query = db.query(models.Article).filter(models.Article.is_published == True)

    if category_id:
        query = query.filter(models.Article.category_id == category_id)
    
    if is_recommended is not None:
        query = query.filter(models.Article.is_recommended == is_recommended)

    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                models.Article.title.ilike(search),
                models.Article.summary.ilike(search)
            )
        )
    
    # 默认按发布时间倒序
    query = query.order_by(models.Article.published_at.desc())
    
    return query.offset(skip).limit(limit).all()

@router.get("/articles/{article_id}", response_model=schemas.ArticleResponse)
def get_article_detail(
    article_id: int,
    db: Session = Depends(get_db)
):
    """
    获取文章详情
    """
    article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 增加阅读量
    article.views += 1
    db.commit()
    db.refresh(article)
    
    return article

@router.post("/articles", response_model=schemas.ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article(
    article: schemas.ArticleCreate,
    db: Session = Depends(get_db)
):
    """
    (管理端) 创建文章
    """
    db_article = models.Article(**article.dict())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article

@router.put("/articles/{article_id}", response_model=schemas.ArticleResponse)
def update_article(
    article_id: int,
    article_update: schemas.ArticleUpdate,
    db: Session = Depends(get_db)
):
    """
    (管理端) 更新文章
    """
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    update_data = article_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_article, key, value)
    
    db.commit()
    db.refresh(db_article)
    return db_article
