from fastapi import APIRouter, Depends, Query, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
import pandas as pd
import io
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/diseases",
    tags=["diseases"]
)

@router.get("/", summary="获取疾病列表")
def get_diseases(
    q: Optional[str] = Query(None, description="搜索关键词（优先搜索诊断名称，其次搜索疾病名称）"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取疾病列表，支持模糊搜索
    优先搜索诊断名称（diagnosis_name），其次搜索其他字段
    """
    query = db.query(models.Disease)
    
    if q:
        search = f"%{q}%"
        # 优先匹配诊断名称和亚目名称
        query = query.filter(
            or_(
                models.Disease.diagnosis_name.ilike(search),
                models.Disease.subcategory_name.ilike(search),
                models.Disease.name.ilike(search),
                models.Disease.code.ilike(search),
                models.Disease.diagnosis_code.ilike(search),
                models.Disease.chapter_name.ilike(search),
                models.Disease.section_name.ilike(search)
            )
        )
    
    total = query.count()
    query = query.order_by(models.Disease.id.desc())
    items = query.offset(skip).limit(limit).all()
    
    return {"items": items, "total": total}

@router.post("/", response_model=schemas.DiseaseResponse, status_code=status.HTTP_201_CREATED)
def create_disease(
    disease: schemas.DiseaseCreate,
    db: Session = Depends(get_db)
):
    """
    创建疾病
    """
    # 如果提供了诊断代码，检查唯一性
    if disease.diagnosis_code:
        exists = db.query(models.Disease).filter(models.Disease.diagnosis_code == disease.diagnosis_code).first()
        if exists:
            raise HTTPException(status_code=400, detail="该诊断代码已存在")
    
    # 兼容性处理：如果没传 category 但传了 chapter_name，自动填充
    db_data = disease.dict()
    if not db_data.get('category') and db_data.get('chapter_name'):
        db_data['category'] = db_data['chapter_name']

    db_disease = models.Disease(**db_data)
    db.add(db_disease)
    db.commit()
    db.refresh(db_disease)
    return db_disease

@router.put("/{disease_id}", response_model=schemas.DiseaseResponse)
def update_disease(
    disease_id: int,
    disease_update: schemas.DiseaseCreate,
    db: Session = Depends(get_db)
):
    """
    更新疾病信息
    """
    db_disease = db.query(models.Disease).filter(models.Disease.id == disease_id).first()
    if not db_disease:
        raise HTTPException(status_code=404, detail="疾病不存在")
    
    # 检查诊断代码唯一性
    if disease_update.diagnosis_code and disease_update.diagnosis_code != db_disease.diagnosis_code:
        exists = db.query(models.Disease).filter(models.Disease.diagnosis_code == disease_update.diagnosis_code).first()
        if exists:
            raise HTTPException(status_code=400, detail="该诊断代码已存在")

    update_data = disease_update.dict(exclude_unset=True)
    
    # 兼容性处理
    if not update_data.get('category') and update_data.get('chapter_name'):
        update_data['category'] = update_data['chapter_name']

    for key, value in update_data.items():
        setattr(db_disease, key, value)
    
    db.commit()
    db.refresh(db_disease)
    return db_disease

@router.delete("/{disease_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_disease(
    disease_id: int,
    db: Session = Depends(get_db)
):
    """
    删除疾病
    """
    db_disease = db.query(models.Disease).filter(models.Disease.id == disease_id).first()
    if not db_disease:
        raise HTTPException(status_code=404, detail="疾病不存在")
    
    db.delete(db_disease)
    db.commit()
    return None

@router.post("/batch-delete", status_code=status.HTTP_200_OK)
def batch_delete_diseases(
    request: schemas.BatchDeleteRequest,
    db: Session = Depends(get_db)
):
    """
    批量删除疾病
    """
    db.query(models.Disease).filter(models.Disease.id.in_(request.ids)).delete(synchronize_session=False)
    db.commit()
    return {"message": f"成功删除 {len(request.ids)} 条数据"}

@router.post("/batch-status", status_code=status.HTTP_200_OK)
def batch_update_status(
    request: schemas.BatchStatusUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    批量更新疾病状态
    """
    db.query(models.Disease).filter(models.Disease.id.in_(request.ids)).update(
        {models.Disease.is_active: request.is_active},
        synchronize_session=False
    )
    db.commit()
    return {"message": f"成功更新 {len(request.ids)} 条数据的状态"}

@router.get("/template")
def download_template():
    """
    下载疾病导入模板 (Excel)
    """
    columns = [
        "章", "章代码范围", "章的名称", "节代码范围", "节名称", 
        "类目代码", "类目名称", "亚目代码", "亚目名称", "诊断代码", "诊断名称", "描述"
    ]
    df = pd.DataFrame(columns=columns)
    
    # Sample row
    sample = {
        "章": "1",
        "章代码范围": "A00-B99",
        "章的名称": "某些传染病和寄生虫病",
        "节代码范围": "A00-A09",
        "节名称": "肠道传染病",
        "类目代码": "A00",
        "类目名称": "霍乱",
        "亚目代码": "A00.0",
        "亚目名称": "霍乱，由于01群霍乱弧菌，霍乱生物型所致",
        "诊断代码": "A00.000",
        "诊断名称": "霍乱，由于01群霍乱弧菌，霍乱生物型所致",
        "描述": "示例描述"
    }
    df = pd.concat([df, pd.DataFrame([sample])], ignore_index=True)
    
    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    stream.seek(0)
    
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=disease_template.xlsx"}
    )

@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_diseases(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    批量导入疾病 (Excel)
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持Excel文件 (.xlsx, .xls)")
    
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # 核心必填项：诊断名称 或 类目名称
        required_cols = ["诊断名称", "类目名称"]
        if not any(col in df.columns for col in required_cols):
             # 兼容旧模板
             if "疾病名称(必填)" not in df.columns:
                raise HTTPException(status_code=400, detail="模板格式错误，缺少核心名称列")
        
        success_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # 提取字段，优先使用新字段名，回退到旧字段名
                name = str(row.get("类目名称", row.get("疾病名称(必填)", ""))).strip()
                code = str(row.get("类目代码", row.get("ICD编码", ""))).strip()
                diagnosis_name = str(row.get("诊断名称", "")).strip()
                diagnosis_code = str(row.get("诊断代码", "")).strip()
                
                # 如果没有类目名称但有诊断名称，用诊断名称填充类目名称
                if (not name or name == 'nan') and (diagnosis_name and diagnosis_name != 'nan'):
                    name = diagnosis_name
                
                if not name or name == 'nan': continue
                
                # 检查重复 (根据诊断代码或诊断名称)
                if diagnosis_code and diagnosis_code != 'nan':
                    exists = db.query(models.Disease).filter(models.Disease.diagnosis_code == diagnosis_code).first()
                    if exists: continue
                
                chapter_name = str(row.get("章的名称", "")).strip()
                
                disease = models.Disease(
                    name=name,
                    code=code if code != 'nan' else None,
                    chapter=str(row.get("章", "")).strip() if str(row.get("章", "")) != 'nan' else None,
                    chapter_code_range=str(row.get("章代码范围", "")).strip() if str(row.get("章代码范围", "")) != 'nan' else None,
                    chapter_name=chapter_name if chapter_name != 'nan' else None,
                    section_code_range=str(row.get("节代码范围", "")).strip() if str(row.get("节代码范围", "")) != 'nan' else None,
                    section_name=str(row.get("节名称", "")).strip() if str(row.get("节名称", "")) != 'nan' else None,
                    subcategory_code=str(row.get("亚目代码", "")).strip() if str(row.get("亚目代码", "")) != 'nan' else None,
                    subcategory_name=str(row.get("亚目名称", "")).strip() if str(row.get("亚目名称", "")) != 'nan' else None,
                    diagnosis_code=diagnosis_code if diagnosis_code != 'nan' else None,
                    diagnosis_name=diagnosis_name if diagnosis_name != 'nan' else None,
                    category=chapter_name if chapter_name != 'nan' else str(row.get("分类(必填)", "")).strip(),
                    description=str(row.get("描述", "")).strip() if str(row.get("描述", "")) != 'nan' else None
                )
                db.add(disease)
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")
        
        db.commit()
        return {"message": f"成功导入 {success_count} 条数据", "errors": errors}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")
