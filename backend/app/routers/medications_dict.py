from fastapi import APIRouter, Depends, Query, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from typing import List, Optional
import pandas as pd
import io
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/medication-dict",
    tags=["medication-dict"]
)

@router.get("/template")
def download_template():
    """
    下载药品导入模板 (Excel)
    """
    columns = [
        "标题", "标题链接", "编号", "r3", "通用名称", "商品名称", "汉语拼音",
        "批准文号", "药品分类", "生产企业", "治疗系统分类", "治疗系统二级分类", "药品性质", "相关疾病",
        "性状", "主要成份", "适应症", "规格", "不良反应",
        "用法用量", "禁忌", "注意事项", "孕妇及哺乳期妇女用药",
        "儿童用药", "老人用药", "药物相互作用", "药理毒理",
        "药代动力学", "贮藏", "有效期"
    ]
    df = pd.DataFrame(columns=columns)
    
    # Sample row
    sample = {
        "标题": "阿莫西林胶囊",
        "标题链接": "",
        "编号": "001",
        "r3": "",
        "通用名称": "阿莫西林",
        "商品名称": "阿莫仙",
        "汉语拼音": "A Mo Xi Lin",
        "批准文号": "国药准字H20052345",
        "药品分类": "化学药品",
        "生产企业": "某制药有限公司",
        "治疗系统分类": "抗感染药物",
        "治疗系统二级分类": "青霉素类抗生素",
        "药品性质": "处方药",
        "相关疾病": "脑膜炎、肺炎",
        "性状": "本品为白色或类白色细粉末",
        "主要成份": "阿莫西林",
        "适应症": "用于敏感菌所致的感染",
        "规格": "0.25g",
        "不良反应": "恶心、呕吐、腹泻",
        "用法用量": "口服。成人一次0.5g，每6-8小时1次",
        "禁忌": "对本品过敏者禁用",
        "注意事项": "请遵医嘱用药",
        "孕妇及哺乳期妇女用药": "在外科医生指导下谨慎使用",
        "儿童用药": "儿童用谨慎",
        "老人用药": "老年人谨慎用药",
        "药物相互作用": "请勿与大环内酯合用",
        "药理毒理": "本品为广谱青霉素类抗生素",
        "药代动力学": "口服后吸收良好",
        "贮藏": "密封，防潮，遮光保存",
        "有效期": "24个月"
    }
    df = pd.concat([df, pd.DataFrame([sample])], ignore_index=True)
    
    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    stream.seek(0)
    
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=medication_template.xlsx"}
    )

@router.post("/import", status_code=status.HTTP_201_CREATED)
async def import_medications(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    批量导入药品 (Excel)
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持Excel文件 (.xlsx, .xls)")
    
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        # Check required columns
        required_cols = ["通用名称"]
        if not any(col in df.columns for col in required_cols):
            raise HTTPException(status_code=400, detail="模板格式错误，缺少\"通用名称\"列")
        
        success_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                generic_name = str(row.get("通用名称", "")).strip()
                trade_name = str(row.get("商品名称", "")).strip()
                approval_number = str(row.get("批准文号", "")).strip()

                if not generic_name or generic_name == 'nan':
                    continue
                
                # Check duplicate
                exists = db.query(models.Medication).filter(
                    models.Medication.generic_name == generic_name,
                    models.Medication.approval_number == (approval_number if approval_number != 'nan' else None)
                ).first()
                if exists:
                    continue 
                
                def _val(key):
                    v = str(row.get(key, "")).strip()
                    return None if v == 'nan' or v == '' else v

                med = models.Medication(
                    title=_val("标题"),
                    title_url=_val("标题链接"),
                    number=_val("编号"),
                    r3=_val("r3"),
                    generic_name=generic_name,
                    trade_name=_val("商品名称"),
                    pinyin=_val("汉语拼音"),
                    approval_number=_val("批准文号"),
                    category=_val("药品分类"),
                    manufacturer=_val("生产企业"),
                    therapeutic_system_category=_val("治疗系统分类"),
                    therapeutic_system_subcategory=_val("治疗系统二级分类"),
                    drug_nature=_val("药品性质"),
                    related_diseases=_val("相关疾病"),
                    properties=_val("性状"),
                    main_ingredients=_val("主要成份"),
                    indications=_val("适应症"),
                    specification=_val("规格"),
                    adverse_reactions=_val("不良反应"),
                    usage_dosage=_val("用法用量"),
                    contraindications=_val("禁忌"),
                    precautions=_val("注意事项"),
                    pregnancy_lactation=_val("孕妇及哺乳期妇女用药"),
                    pediatric_use=_val("儿童用药"),
                    geriatric_use=_val("老人用药"),
                    drug_interactions=_val("药物相互作用"),
                    pharmacology_toxicology=_val("药理毒理"),
                    pharmacokinetics=_val("药代动力学"),
                    storage=_val("贮藏"),
                    expiry_period=_val("有效期"),
                    status="active"
                )
                db.add(med)
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")
        
        db.commit()
        return {"message": f"成功导入 {success_count} 条数据", "errors": errors}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")

@router.get("/", summary="获取药品字典列表")
def get_medications(
    q: Optional[str] = Query(None, description="搜索关键词（通用名称、商品名称）"),
    manufacturer: Optional[str] = Query(None, description="生产企业搜索"),
    category: Optional[str] = Query(None, description="治疗系统二级分类筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取药品字典列表
    """
    query = db.query(models.Medication)

    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                models.Medication.generic_name.ilike(search),
                models.Medication.trade_name.ilike(search)
            )
        )
    
    if manufacturer:
        search_manufacturer = f"%{manufacturer}%"
        query = query.filter(models.Medication.manufacturer.ilike(search_manufacturer))
    
    if category:
        query = query.filter(models.Medication.therapeutic_system_subcategory == category)
        
    if status:
        query = query.filter(models.Medication.status == status)
    
    total = query.count()
    query = query.order_by(models.Medication.id.desc())
    items = query.offset(skip).limit(limit).all()
    
    return {"items": items, "total": total}

@router.get("/categories", summary="获取治疗系统二级分类列表")
def get_medication_categories(
    db: Session = Depends(get_db)
):
    """
    获取所有治疗系统二级分类（用于筛选下拉框）
    """
    categories = db.query(models.Medication.therapeutic_system_subcategory).filter(
        models.Medication.therapeutic_system_subcategory.isnot(None),
        models.Medication.therapeutic_system_subcategory != ''
    ).distinct().all()
    
    return {"items": [c[0] for c in categories]}

@router.get("/category-tree", summary="获取药品分类树")
def get_category_tree(
    db: Session = Depends(get_db)
):
    """
    获取药品分类树（一级分类和二级分类）
    """
    # Get all categories with their subcategories
    meds = db.query(
        models.Medication.therapeutic_system_category,
        models.Medication.therapeutic_system_subcategory
    ).filter(
        models.Medication.therapeutic_system_category.isnot(None),
        models.Medication.therapeutic_system_category != '',
        models.Medication.therapeutic_system_subcategory.isnot(None),
        models.Medication.therapeutic_system_subcategory != ''
    ).distinct().all()
    
    # Build tree structure
    tree = {}
    for cat, subcat in meds:
        if cat not in tree:
            tree[cat] = set()
        tree[cat].add(subcat)
    
    # Convert to list
    result = []
    for cat in sorted(tree.keys()):
        result.append({
            "name": cat,
            "subcategories": sorted(list(tree[cat]))
        })
    
    return result

@router.get("/search-all", summary="全局搜索药品和疾病")
def search_all(
    q: str = Query(..., description="搜索关键词"),
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    全局搜索药品和疾病
    """
    results = []
    search = f"%{q}%"
    
    # Search medications
    meds = db.query(models.Medication).filter(
        or_(
            models.Medication.generic_name.ilike(search),
            models.Medication.trade_name.ilike(search),
            models.Medication.related_diseases.ilike(search)
        ),
        models.Medication.status == 'active'
    ).limit(limit).all()
    
    for med in meds:
        results.append({
            "type": "medication",
            "id": med.id,
            "name": med.generic_name or med.title,
            "sub_name": med.trade_name,
            "category": med.therapeutic_system_subcategory,
            "manufacturer": med.manufacturer,
            "specification": med.specification
        })
    
    # Search diseases
    diseases = db.query(models.Disease).filter(
        or_(
            models.Disease.name.ilike(search),
            models.Disease.diagnosis_name.ilike(search)
        ),
        models.Disease.is_active == True
    ).limit(limit).all()
    
    for disease in diseases:
        results.append({
            "type": "disease",
            "id": disease.id,
            "name": disease.name,
            "category": disease.chapter_name or disease.category,
            "section": disease.section_name
        })
    
    return {"items": results, "total": len(results)}

@router.get("/{med_id}", summary="获取药品详情")
def get_medication_detail(
    med_id: int,
    db: Session = Depends(get_db)
):
    """
    获取单个药品详情
    """
    med = db.query(models.Medication).filter(models.Medication.id == med_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="药品不存在")
    return med


@router.post("/", response_model=schemas.MedicationResponse, status_code=status.HTTP_201_CREATED)
def create_medication(
    medication: schemas.MedicationCreate,
    db: Session = Depends(get_db)
):
    """
    创建药品
    """
    # Check duplicate
    exists = db.query(models.Medication).filter(
        models.Medication.generic_name == medication.generic_name,
        models.Medication.specification == medication.specification
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="该药品已存在")
        
    db_med = models.Medication(**medication.dict())
    db.add(db_med)
    db.commit()
    db.refresh(db_med)
    return db_med

@router.put("/{med_id}", response_model=schemas.MedicationResponse)
def update_medication(
    med_id: int,
    med_update: schemas.MedicationUpdate,
    db: Session = Depends(get_db)
):
    """
    更新药品信息
    """
    db_med = db.query(models.Medication).filter(models.Medication.id == med_id).first()
    if not db_med:
        raise HTTPException(status_code=404, detail="药品不存在")
    
    update_data = med_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_med, key, value)
    
    db.commit()
    db.refresh(db_med)
    return db_med

@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication(
    medication_id: int,
    db: Session = Depends(get_db)
):
    """
    删除药品
    """
    db_med = db.query(models.Medication).filter(models.Medication.id == medication_id).first()
    if not db_med:
        raise HTTPException(status_code=404, detail="药品不存在")
    
    db.delete(db_med)
    db.commit()
    return None

@router.post("/batch-delete", status_code=status.HTTP_200_OK)
def batch_delete_medications(
    request: schemas.BatchDeleteRequest,
    db: Session = Depends(get_db)
):
    """
    批量删除药品
    """
    db.query(models.Medication).filter(models.Medication.id.in_(request.ids)).delete(synchronize_session=False)
    db.commit()
    return {"message": f"成功删除 {len(request.ids)} 条数据"}

@router.post("/batch-status", status_code=status.HTTP_200_OK)
def batch_update_status(
    request: schemas.BatchStatusUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    批量更新药品状态
    """
    # Map active/inactive to whatever frontend sends, usually boolean or string
    # Assuming frontend sends boolean is_active, but Medication model uses string status='active'/'inactive'
    status_str = "active" if request.is_active else "inactive"
    
    db.query(models.Medication).filter(models.Medication.id.in_(request.ids)).update(
        {models.Medication.status: status_str},
        synchronize_session=False
    )
    db.commit()
    return {"message": f"成功更新 {len(request.ids)} 条数据的状态"}
