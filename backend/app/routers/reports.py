from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import ocr_service
from app.services.minio_service import minio_service
from app.config import settings
from app import crud, models, dependencies, schemas
from typing import Optional, List
from pydantic import UUID4
from datetime import date
import datetime
import httpx
from sqlalchemy import func

router = APIRouter(
    prefix="/reports",
    tags=["reports"]
)

@router.get("/trends", response_model=List[schemas.MetricTrendResponse])
def get_report_trends(
    patient_id: Optional[UUID4] = None,
    member_id: Optional[UUID4] = None,
    report_type: Optional[str] = None,
    metric_names: Optional[List[str]] = Query(None),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    获取指标趋势数据
    支持按成员筛选，如未指定成员则使用当前成员
    """
    target_patient_id = patient_id
    target_member_id = member_id
    
    if current_user.role == models.UserRole.patient:
        patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile not found")
        target_patient_id = patient.id
        
        if not target_member_id:
            current_member = db.query(models.Member).filter(
                models.Member.patient_id == patient.id,
                models.Member.is_current == True
            ).first()
            if current_member:
                target_member_id = current_member.id
    elif not target_patient_id:
        raise HTTPException(status_code=400, detail="Patient ID is required for non-patient users")

    query = db.query(
        models.ReportMetric.name,
        models.ReportMetric.value,
        models.ReportMetric.unit,
        models.ReportMetric.is_abnormal,
        models.Report.report_date
    ).join(
        models.Report, models.ReportMetric.report_id == models.Report.id
    ).filter(
        models.Report.patient_id == target_patient_id
    )

    if target_member_id:
        query = query.filter(models.Report.member_id == target_member_id)
    else:
        query = query.filter(
            (models.Report.member_id == None) | 
            (models.Report.member_id == target_member_id)
        )

    if report_type:
        query = query.filter(models.Report.report_type == report_type)

    if metric_names:
        query = query.filter(models.ReportMetric.name.in_(metric_names))
    
    if start_date:
        query = query.filter(models.Report.report_date >= start_date)
    if end_date:
        query = query.filter(models.Report.report_date <= end_date)

    query = query.order_by(models.Report.report_date.asc())

    results = query.all()

    trends_map = {}
    for name, value, unit, is_abnormal, report_date in results:
        if name not in trends_map:
            trends_map[name] = {
                "metric_name": name,
                "unit": unit,
                "points": []
            }
        
        try:
            import re
            match = re.search(r"[-+]?\d*\.\d+|\d+", str(value))
            if match:
                numeric_val = float(match.group())
                trends_map[name]["points"].append({
                    "date": report_date,
                    "value": numeric_val,
                    "unit": unit,
                    "is_abnormal": is_abnormal or False
                })
        except Exception:
            continue

    # 4. Filter for "at least 2 points" requirement? 
    # User said "must be two or more to form a trend chart".
    # We will return all, frontend decides what to render.
    
    return list(trends_map.values())

@router.post("/parse")
async def parse_report(
    file: UploadFile = File(...),
    report_type_id: Optional[int] = Form(None),
    hospital_id: Optional[int] = Form(None),
    patient_disease_id: Optional[int] = Form(None),
    patient_id: Optional[UUID4] = Form(None), # For doctors uploading for patients
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    print(f"Received report upload request: filename={file.filename}, type={file.content_type}")
    print(f"Form data: patient_disease_id={patient_disease_id}, hospital_id={hospital_id}")

    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    content = await file.read()
    print(f"File content read, size: {len(content)} bytes")
    
    try:
        bucket = (
            (settings.MINIO_BUCKET_MEDICAL or "binli")
            if patient_disease_id
            else (settings.MINIO_BUCKET_REPORT or "jianchabaogao")
        )
        minio_url, object_name = minio_service.upload_file(content, file.filename, file.content_type, bucket_name=bucket)
        print(f"MinIO upload successful: {minio_url}")
    except Exception as e:
        print(f"MinIO upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file to storage: {str(e)}")

    try:
        print("Calling OCR service...")
        parsed_data = await ocr_service.parse_report_file(content, file.filename)
        print("OCR service returned data")
    except Exception as e:
        print(f"Parsing error: {e}")
        import traceback
        traceback.print_exc()
        if isinstance(e, (httpx.ReadTimeout, httpx.ConnectTimeout)):
            raise HTTPException(status_code=504, detail="OCR服务超时，请稍后重试")
        msg = str(e) if e else ""
        if "readtimeout" in msg.lower() or "timeout" in msg.lower():
            raise HTTPException(status_code=504, detail="OCR服务超时，请稍后重试")
        raise HTTPException(status_code=500, detail="解析失败，请稍后重试")
    
    hospital_name = ""
    if hospital_id:
        hospital = crud.get_hospital(db, hospital_id)
        if hospital:
            hospital_name = hospital.name
            
    if parsed_data.get("hospital_name"):
        hospital_name = parsed_data["hospital_name"]
    
    parsed_data["hospital_name"] = hospital_name
    parsed_data["image_url"] = minio_url
    parsed_data["file_name"] = file.filename

    return parsed_data

@router.post("/parse-imaging")
async def parse_imaging_report(
    file: UploadFile = File(...),
    imaging_check_id: str = Form(...),
    hospital_id: Optional[int] = Form(None),
    patient_disease_id: Optional[int] = Form(None),
    patient_id: Optional[UUID4] = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    content = await file.read()

    try:
        bucket = (
            (settings.MINIO_BUCKET_MEDICAL or "binli")
            if patient_disease_id
            else (settings.MINIO_BUCKET_REPORT or "jianchabaogao")
        )
        minio_url, _ = minio_service.upload_file(content, file.filename, file.content_type, bucket_name=bucket)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file to storage: {str(e)}")

    try:
        parsed_data = await ocr_service.parse_report_text_only(content, file.filename)
    except Exception as e:
        if isinstance(e, (httpx.ReadTimeout, httpx.ConnectTimeout)):
            raise HTTPException(status_code=504, detail="OCR服务超时，请稍后重试")
        msg = str(e) if e else ""
        if "readtimeout" in msg.lower() or "timeout" in msg.lower():
            raise HTTPException(status_code=504, detail="OCR服务超时，请稍后重试")
        raise HTTPException(status_code=500, detail="解析失败，请稍后重试")

    hospital_name = ""
    if hospital_id:
        hospital = crud.get_hospital(db, hospital_id)
        if hospital:
            hospital_name = hospital.name

    imaging_check = db.query(models.HospitalImagingCheck).filter(models.HospitalImagingCheck.check_id == imaging_check_id).first()
    imaging_data = None
    if imaging_check:
        imaging_data = {
            "check_id": imaging_check.check_id,
            "check_category": imaging_check.check_category,
            "check_subcategory": imaging_check.check_subcategory,
            "check_part": imaging_check.check_part,
            "is_enhanced": int(imaging_check.is_enhanced or 0),
            "applicable_gender": imaging_check.applicable_gender,
            "check_desc": imaging_check.check_desc,
            "department": imaging_check.department,
            "sort_num": imaging_check.sort_num
        }

    return {
        "report_date": parsed_data.get("report_date"),
        "hospital_name": hospital_name,
        "text": parsed_data.get("text"),
        "image_url": minio_url,
        "file_name": file.filename,
        "imaging_check": imaging_data
    }

@router.get("/{report_id}", response_model=schemas.ReportResponse)
def read_report(
    report_id: UUID4,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    Get a specific report by ID
    """
    report = crud.get_report(db, report_id=report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
        
    # Check permissions: User must own the report (via patient) or be a doctor/admin
    if current_user.role == models.UserRole.patient:
        # Check if report belongs to this patient
        if report.patient.user_id != current_user.id:
             raise HTTPException(status_code=403, detail="Not authorized to view this report")
             
    return report

@router.put("/{report_id}", response_model=schemas.ReportResponse)
def update_report(
    report_id: UUID4,
    report_update: schemas.ReportUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    Update a report's metadata (e.g. after user confirmation)
    """
    # 1. Find report
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    # 2. Check permission
    # If patient, must be their report
    if current_user.role == models.UserRole.patient:
        patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
        if not patient or report.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this report")
    
    # 3. Update fields
    if report_update.hospital_name is not None:
        report.hospital_name = report_update.hospital_name
    if report_update.report_date is not None:
        report.report_date = report_update.report_date
    if report_update.summary is not None:
        report.summary = report_update.summary
    if report_update.patient_disease_id is not None:
        report.patient_disease_id = report_update.patient_disease_id
        
    if report_update.metrics is not None:
        # Update metrics: delete old ones and re-insert new ones
        # This is simpler than diffing for now
        for old_metric in report.metrics:
            db.delete(old_metric)
        
        for m in report_update.metrics:
            new_metric = models.ReportMetric(
                report_id=report.id,
                name=m.name,
                code=m.code,
                value=m.value,
                unit=m.unit,
                reference_range=m.reference_range,
                is_abnormal=m.is_abnormal,
                abnormal_symbol=m.abnormal_symbol
            )
            db.add(new_metric)

    db.commit()
    db.refresh(report)
    return report

@router.delete("/{report_id}", status_code=204)
def delete_report(
    report_id: UUID4,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    Delete a report
    """
    # 1. Find report
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    # 2. Check permission
    # If patient, must be their report
    if current_user.role == models.UserRole.patient:
        patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
        if not patient or report.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this report")
            
    # 3. Delete
    success = crud.delete_report(db, report_id=report_id)
    if not success:
         raise HTTPException(status_code=500, detail="Failed to delete report")
    
    return

LAB_KEYWORDS = [
    '血常规', '尿常规', '肝功能', '肾功能', '血糖', '血脂', '电解质',
    '甲状腺', '凝血', '心肌酶', '肿瘤标志物', '乙肝', '丙肝', 'HIV',
    '血型', '贫血', '铁蛋白', '维生素', '激素', '免疫', '抗体',
    '白细胞', '红细胞', '血小板', '血红蛋白', '谷丙', '谷草', '肌酐',
    '尿素', '尿酸', '胆固醇', '甘油三酯', '血糖', '糖化血红蛋白',
    '化验', '检验', '检测', '标本', '血清', '血浆', '全血', '参考值', '结果'
]

IMAGING_KEYWORDS = [
    'CT', 'MRI', '核磁', 'X光', '胸片', '超声', 'B超', '彩超',
    '影像', '放射', '扫描', '透视', '造影', 'PET', 'SPECT',
    '影像科', '放射科', '超声科', '介入', 'CT室', 'MRI室',
    '印象', '结论', '诊断意见', '检查所见', '胶片',
    '检查部位', '检查方式', '检查方法', '影像表现'
]

def classify_report_by_text(text: str, metrics_count: int = 0) -> str:
    """
    根据文本内容自动分类报告
    返回分类类型: 'lab' - 化验单, 'imaging' - 影像报告, 'unknown' - 未分类
    """
    if not text:
        return 'unknown'
    
    if metrics_count >= 1:
        return 'lab'
    
    text_lower = text.lower()
    
    lab_score = sum(1 for kw in LAB_KEYWORDS if kw.lower() in text_lower)
    imaging_score = sum(1 for kw in IMAGING_KEYWORDS if kw.lower() in text_lower)
    
    if lab_score > imaging_score:
        return 'lab'
    elif imaging_score > lab_score and imaging_score >= 2:
        return 'imaging'
    elif lab_score >= 1:
        return 'lab'
    else:
        return 'unknown'

@router.post("/auto-classify")
async def auto_classify_report(
    file: UploadFile = File(...),
    member_id: Optional[UUID4] = Form(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    自动分类上传报告
    流程:
    1. 上传文件到MinIO
    2. OCR解析文本和指标
    3. 自动分类判定（化验单/影像报告/未分类）
    4. 保存到数据库（包括结构化指标）
    5. 返回结果
    """
    if not file:
        raise HTTPException(status_code=400, detail="请选择要上传的图片")
    
    content = await file.read()
    
    try:
        bucket = settings.MINIO_BUCKET_REPORT or "jianchabaogao"
        minio_url, object_name = minio_service.upload_file(
            content, 
            file.filename, 
            file.content_type, 
            bucket_name=bucket
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="上传失败，请重试")
    
    ocr_text = ""
    parsed_metrics = []
    hospital_name = ""
    report_date = datetime.date.today()
    basic_info = {}
    findings = ""
    diagnosis = ""
    
    try:
        parsed_data = await ocr_service.parse_report_file(content, file.filename)
        ocr_text = parsed_data.get("summary", "")
        parsed_metrics = parsed_data.get("metrics", [])
        hospital_name = parsed_data.get("hospital_name", "")
        basic_info = parsed_data.get("basic_info", {})
        findings = parsed_data.get("findings", "")
        diagnosis = parsed_data.get("diagnosis", "")
        if parsed_data.get("report_date"):
            try:
                report_date = datetime.datetime.strptime(parsed_data["report_date"], "%Y-%m-%d").date()
            except:
                pass
    except Exception as e:
        if isinstance(e, (httpx.ReadTimeout, httpx.ConnectTimeout)):
            raise HTTPException(status_code=504, detail="OCR服务超时，请稍后重试")
        msg = str(e) if e else ""
        if "readtimeout" in msg.lower() or "timeout" in msg.lower():
            raise HTTPException(status_code=504, detail="OCR服务超时，请稍后重试")
        pass
    
    report_category = classify_report_by_text(ocr_text, len(parsed_metrics))
    
    try:
        if current_user.role == models.UserRole.patient:
            patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
            if not patient:
                raise HTTPException(status_code=404, detail="Patient profile not found")
            patient_id = patient.id
            
            if not member_id:
                current_member = db.query(models.Member).filter(
                    models.Member.patient_id == patient.id,
                    models.Member.is_current == True
                ).first()
                member_id = current_member.id if current_member else None
        else:
            raise HTTPException(status_code=403, detail="Only patients can upload reports")
        
        category_names = {
            'lab': '化验单',
            'imaging': '影像报告',
            'unknown': '未分类'
        }
        report_type_name = category_names.get(report_category, '未分类')
        
        report_data = {"ocr_text": ocr_text, "category": report_category}
        report_data.update(basic_info)
        
        if findings:
            report_data["findings"] = findings
        if diagnosis:
            report_data["diagnosis"] = diagnosis
        
        report = models.Report(
            patient_id=patient_id,
            member_id=member_id,
            report_date=report_date,
            hospital_name=hospital_name,
            report_type=report_type_name,
            image_url=minio_url,
            file_name=file.filename,
            status=models.ReportStatus.normal,
            data=report_data,
            summary=ocr_text[:2000] if ocr_text else ""
        )
        db.add(report)
        db.flush()
        
        if parsed_metrics and len(parsed_metrics) > 0:
            for metric_data in parsed_metrics:
                metric = models.ReportMetric(
                    report_id=report.id,
                    name=str(metric_data.get("name", ""))[:100],
                    code=str(metric_data.get("code", ""))[:50] if metric_data.get("code") else None,
                    value=str(metric_data.get("value", ""))[:50],
                    unit=str(metric_data.get("unit", ""))[:50] if metric_data.get("unit") else None,
                    reference_range=str(metric_data.get("range", ""))[:100] if metric_data.get("range") else None,
                    is_abnormal=bool(metric_data.get("abnormal", False)),
                    abnormal_symbol=str(metric_data.get("abnormal_symbol", ""))[:10] if metric_data.get("abnormal_symbol") else None
                )
                db.add(metric)
        
        db.commit()
        db.refresh(report)
        
        message = "上传成功"
        if report_category == 'unknown':
            message = "无法自动识别类型，已标记为未分类"
        
        return {
            "success": True,
            "report_id": str(report.id),
            "category": report_category,
            "metrics_count": len(parsed_metrics),
            "message": message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error saving report: {e}")
        raise HTTPException(status_code=500, detail="上传失败，请重试")
