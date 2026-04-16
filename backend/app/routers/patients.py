from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import UUID4
from datetime import date, timedelta
from .. import crud, schemas, models, dependencies
from ..binding_manager import manager as binding_manager

router = APIRouter(
    prefix="/patients",
    tags=["patients"],
)

@router.get("/notifications", response_model=schemas.PatientNotificationResponse, summary="获取患者通知", description="获取复诊倒计时(7天内)和用药倒计时(3天内)的消息。")
def get_notifications(current_user: models.User = Depends(dependencies.get_current_active_user), db: Session = Depends(dependencies.get_db)):
    """
    获取患者个人通知
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
        
    today = date.today()
    notifications = []
    
    # 1. 复诊通知 (未来7天)
    revisit_plans = db.query(models.RevisitPlan).filter(
        models.RevisitPlan.patient_id == patient.id,
        models.RevisitPlan.is_active == True,
        models.RevisitPlan.next_date >= today,
        models.RevisitPlan.next_date <= today + timedelta(days=7)
    ).all()
    
    for plan in revisit_plans:
        days_left = (plan.next_date - today).days
        disease_name = plan.patient_disease.name if plan.patient_disease else "通用"
        member_nickname = plan.member.nickname if plan.member else None
        member_relation = plan.member.relation if plan.member else None
        member_id = plan.member_id
        notifications.append(schemas.PatientNotificationItem(
            id=f"revisit-{plan.id}",
            type="revisit",
            title="复诊提醒",
            content=f"您的{disease_name}复诊计划即将在 {plan.next_date} 进行，还有 {days_left} 天。",
            days_left=days_left,
            notification_date=plan.next_date,
            member_id=member_id,
            member_nickname=member_nickname,
            member_relation=member_relation
        ))
        
    # 2. 用药余量通知 (未来3天)
    # 基于 MedicationPlan.end_date
    med_plans = db.query(models.MedicationPlan).filter(
        models.MedicationPlan.patient_id == patient.id,
        models.MedicationPlan.is_active == True,
        models.MedicationPlan.end_date >= today,
        models.MedicationPlan.end_date <= today + timedelta(days=3)
    ).all()
    
    for plan in med_plans:
        days_left = (plan.end_date - today).days
        member_nickname = plan.member.nickname if plan.member else None
        member_relation = plan.member.relation if plan.member else None
        member_id = plan.member_id
        notifications.append(schemas.PatientNotificationItem(
            id=f"med-{plan.id}",
            type="medication",
            title="药品余量不足",
            content=f"您的药品 {plan.name} 余量即将用完（截止日期 {plan.end_date}），请及时补充。还有 {days_left} 天用量。",
            days_left=days_left,
            notification_date=plan.end_date,
            member_id=member_id,
            member_nickname=member_nickname,
            member_relation=member_relation
        ))
        
    # 按剩余天数排序
    notifications.sort(key=lambda x: x.days_left)
    
    return {
        "items": notifications,
        "count": len(notifications)
    }

@router.post("/binding-code", response_model=schemas.BindingCodeResponse, summary="生成医生绑定码", description="生成一个用于医生绑定的6位数字验证码，有效期5分钟。")
def generate_binding_code(current_user: models.User = Depends(dependencies.get_current_active_user), db: Session = Depends(dependencies.get_db)):
    """
    生成绑定码
    """
    # 验证用户角色
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
        
    code = binding_manager.generate_code(patient.id)
    return {"code": code, "expires_in": binding_manager.EXPIRATION_SECONDS}

@router.get("/", summary="获取所有患者列表(管理员)", description="获取系统所有患者列表，支持分页和搜索。")
def get_all_patients(
    skip: int = 0, 
    limit: int = 20, 
    q: str | None = None,
    current_user: models.User = Depends(dependencies.get_current_active_user), 
    db: Session = Depends(dependencies.get_db)
):
    """
    获取所有患者列表 (管理员权限)
    """
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = db.query(models.Patient)
    if q:
        search = f"%{q}%"
        query = query.filter(models.Patient.name.ilike(search) | models.Patient.user.has(models.User.phone.ilike(search)))
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return {"items": items, "total": total}

@router.get("/me", response_model=schemas.PatientResponse, summary="获取当前患者信息", description="获取当前登录患者的个人详细档案。")
def read_patient_me(current_user: models.User = Depends(dependencies.get_current_active_user), db: Session = Depends(dependencies.get_db)):
    """
    获取患者个人信息
    需要患者权限
    """
    # 验证用户角色
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # 查询患者档案
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return patient

@router.post("/diseases", response_model=schemas.PatientDiseaseResponse, summary="添加慢性病记录", description="为当前患者添加一条慢性病确诊记录。")
def add_disease(
    disease_data: schemas.PatientDiseaseCreate, 
    current_user: models.User = Depends(dependencies.get_current_active_user), 
    db: Session = Depends(dependencies.get_db)
):
    """
    添加慢性病记录
    自动关联当前成员（如未指定）
    """
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    if not disease_data.member_id:
        current_member = db.query(models.Member).filter(
            models.Member.patient_id == patient.id,
            models.Member.is_current == True
        ).first()
        if current_member:
            disease_data.member_id = current_member.id
    
    return crud.add_patient_disease(db, patient_id=patient.id, disease_data=disease_data)

@router.get("/diseases", response_model=List[schemas.PatientDiseaseResponse], summary="获取我的慢性病列表", description="获取当前患者所有已记录的慢性病信息。")
def get_my_diseases(
    member_id: Optional[UUID4] = None,
    current_user: models.User = Depends(dependencies.get_current_active_user), 
    db: Session = Depends(dependencies.get_db)
):
    """
    查询我的慢性病列表
    支持按成员筛选，如未指定则使用当前成员
    """
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    target_member_id = member_id
    if not target_member_id:
        current_member = db.query(models.Member).filter(
            models.Member.patient_id == patient.id,
            models.Member.is_current == True
        ).first()
        if current_member:
            target_member_id = current_member.id
    
    diseases = crud.get_patient_diseases(db, patient_id=patient.id)
    
    if target_member_id:
        diseases = [d for d in diseases if d.member_id == target_member_id]
    else:
        diseases = [d for d in diseases if d.member_id is None or d.member_id == target_member_id]
    
    return diseases

@router.put("/diseases/{disease_id}", response_model=schemas.PatientDiseaseResponse, summary="更新慢性病记录", description="更新已有的慢性病记录。")
def update_disease(disease_id: int, disease_update: schemas.PatientDiseaseUpdate, current_user: models.User = Depends(dependencies.get_current_active_user), db: Session = Depends(dependencies.get_db)):
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    # Ensure the disease record belongs to this patient
    existing_disease = db.query(models.PatientDisease).filter(models.PatientDisease.id == disease_id, models.PatientDisease.patient_id == patient.id).first()
    if not existing_disease:
        raise HTTPException(status_code=404, detail="Disease record not found")

    return crud.update_patient_disease(db, disease_id=disease_id, disease_update=disease_update)

@router.delete("/diseases/{disease_id}", summary="删除慢性病记录", description="删除已有的慢性病记录。")
def delete_disease(disease_id: int, current_user: models.User = Depends(dependencies.get_current_active_user), db: Session = Depends(dependencies.get_db)):
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    # Ensure the disease record belongs to this patient
    existing_disease = db.query(models.PatientDisease).filter(models.PatientDisease.id == disease_id, models.PatientDisease.patient_id == patient.id).first()
    if not existing_disease:
        raise HTTPException(status_code=404, detail="Disease record not found")

    crud.delete_patient_disease(db, disease_id=disease_id)
    return {"message": "Successfully deleted"}

@router.post("/reports", response_model=schemas.ReportResponse, summary="上传检查报告", description="上传新的检查报告记录（含OCR数据）。")
def upload_report(
    report: schemas.ReportCreate, 
    current_user: models.User = Depends(dependencies.get_current_active_user), 
    db: Session = Depends(dependencies.get_db)
):
    """
    上传检查报告
    - 验证报告归属权
    - 自动关联当前成员（如未指定）
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
        
    if report.patient_id != patient.id:
        raise HTTPException(status_code=403, detail="Cannot upload report for another patient")
    
    if not report.member_id:
        current_member = db.query(models.Member).filter(
            models.Member.patient_id == patient.id,
            models.Member.is_current == True
        ).first()
        if current_member:
            report.member_id = current_member.id
    
    return crud.create_report(db, report=report)

@router.post("/reports/parse", response_model=schemas.ReportParseResponse, summary="解析检查报告", description="上传报告文件进行OCR解析（模拟）。")
def parse_report(
    file: UploadFile = File(...),
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    解析检查报告（模拟OCR）
    """
    import datetime
    import random
    
    # 模拟OCR解析延迟
    # time.sleep(1)
    
    # 根据文件名或随机生成模拟数据
    # 实际项目中应调用OCR服务
    
    mock_metrics = [
        {"name": "白细胞计数(WBC)", "value": "7.2", "unit": "10^9/L", "status": "normal", "range": "3.5-9.5"},
        {"name": "红细胞计数(RBC)", "value": "4.8", "unit": "10^12/L", "status": "normal", "range": "4.0-5.5"},
        {"name": "血红蛋白(HGB)", "value": "142", "unit": "g/L", "status": "normal", "range": "120-160"},
        {"name": "血小板计数(PLT)", "value": "225", "unit": "10^9/L", "status": "normal", "range": "100-300"},
        {"name": "中性粒细胞百分比", "value": "65.0", "unit": "%", "status": "normal", "range": "40-75"},
    ]
    
    return {
        "hospital_name": "北京协和医院",
        "report_date": datetime.date.today(),
        "metrics": mock_metrics,
        "summary": "血常规各项指标正常。"
    }

@router.get("/reports", response_model=List[schemas.ReportResponse], summary="获取我的报告列表", description="获取当前患者的历史检查报告列表。支持按类型过滤。")
def get_my_reports(
    type: str | None = None,
    member_id: Optional[UUID4] = None,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    """
    查询我的历史报告
    支持按成员筛选，如未指定则使用当前成员
    支持按类型筛选：
    - type='check': 检查报告（report_type != '病历报告'）
    - type='medical': 病历报告（report_type == '病历报告'）
    - type=None: 所有报告
    """
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    target_member_id = member_id
    if not target_member_id:
        current_member = db.query(models.Member).filter(
            models.Member.patient_id == patient.id,
            models.Member.is_current == True
        ).first()
        if current_member:
            target_member_id = current_member.id
    
    query = db.query(models.Report).filter(models.Report.patient_id == patient.id)
    
    if type == "check":
        query = query.filter(models.Report.report_type != '病历报告')
    elif type == "medical":
        query = query.filter(models.Report.report_type == '病历报告')
    
    reports = query.order_by(models.Report.report_date.desc()).all()
    
    if target_member_id:
        reports = [r for r in reports if r.member_id == target_member_id]
    else:
        reports = [r for r in reports if r.member_id is None or r.member_id == target_member_id]
    
    return reports

@router.post("/readings", response_model=schemas.HealthReadingResponse, summary="录入健康数据", description="录入血压、血糖、体重等健康指标数据。")
def add_reading(
    reading: schemas.HealthReadingCreate, 
    current_user: models.User = Depends(dependencies.get_current_active_user), 
    db: Session = Depends(dependencies.get_db)
):
    """
    录入健康监测数据
    自动关联当前成员（如未指定）
    """
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    if not reading.member_id:
        current_member = db.query(models.Member).filter(
            models.Member.patient_id == patient.id,
            models.Member.is_current == True
        ).first()
        if current_member:
            reading.member_id = current_member.id
    
    return crud.create_health_reading(db, reading, patient_id=patient.id)

@router.get("/readings/{type}", response_model=List[schemas.HealthReadingResponse], summary="获取特定类型的健康趋势", description="根据类型（如 blood_pressure）获取历史健康数据。")
def get_readings_by_type(
    type: str, 
    member_id: Optional[UUID4] = None,
    current_user: models.User = Depends(dependencies.get_current_active_user), 
    db: Session = Depends(dependencies.get_db)
):
    """
    获取特定类型的健康趋势数据
    支持按成员筛选，如未指定则使用当前成员
    """
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    target_member_id = member_id
    if not target_member_id:
        current_member = db.query(models.Member).filter(
            models.Member.patient_id == patient.id,
            models.Member.is_current == True
        ).first()
        if current_member:
            target_member_id = current_member.id
    
    readings = crud.get_patient_readings(db, patient_id=patient.id, type=type)
    
    if target_member_id:
        readings = [r for r in readings if r.member_id == target_member_id]
    else:
        readings = [r for r in readings if r.member_id is None or r.member_id == target_member_id]
    
    return readings

@router.get("/doctors", response_model=List[schemas.BindingResponse], summary="获取我的医生", description="获取当前患者已绑定的医生列表。")
def get_my_doctors(current_user: models.User = Depends(dependencies.get_current_active_user), db: Session = Depends(dependencies.get_db)):
    """
    查询已绑定的医生列表
    """
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    return crud.get_patient_doctors(db, patient_id=patient.id)

# --- Reminders ---
@router.get("/diseases/{patient_disease_id}/reminders", response_model=List[schemas.ReminderResponse], summary="获取提醒列表", description="获取某慢性病的提醒列表。")
def get_reminders(patient_disease_id: int, current_user: models.User = Depends(dependencies.get_current_active_user), db: Session = Depends(dependencies.get_db)):
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return crud.get_reminders_by_disease(db, patient_id=patient.id, patient_disease_id=patient_disease_id)

@router.post("/diseases/{patient_disease_id}/reminders", response_model=schemas.ReminderResponse, summary="添加提醒", description="为某慢性病添加吃药或复查提醒。")
def add_reminder(patient_disease_id: int, reminder: schemas.ReminderCreate, current_user: models.User = Depends(dependencies.get_current_active_user), db: Session = Depends(dependencies.get_db)):
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    if reminder.patient_disease_id != patient_disease_id:
        raise HTTPException(status_code=400, detail="Mismatch disease id")
    return crud.create_reminder(db, patient_id=patient.id, reminder=reminder)

@router.delete("/reminders/{reminder_id}", summary="删除提醒", description="删除提醒项。")
def remove_reminder(reminder_id: int, current_user: models.User = Depends(dependencies.get_current_active_user), db: Session = Depends(dependencies.get_db)):
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    ok = crud.delete_reminder(db, patient_id=patient.id, reminder_id=reminder_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Successfully deleted"}

@router.put("/reminders/{reminder_id}", response_model=schemas.ReminderResponse, summary="更新提醒", description="更新提醒的标题、计划文本、是否启用等字段。")
def update_reminder(reminder_id: int, reminder: schemas.ReminderCreateOptional, current_user: models.User = Depends(dependencies.get_current_active_user), db: Session = Depends(dependencies.get_db)):
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    existing = db.query(models.Reminder).filter(models.Reminder.id == reminder_id, models.Reminder.patient_id == patient.id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Reminder not found")
    existing.title = reminder.title
    existing.schedule_text = reminder.schedule_text
    existing.is_active = reminder.is_active
    if reminder.end_date:
        existing.end_date = reminder.end_date
    db.commit()
    db.refresh(existing)
    return existing

@router.get("/reminders", response_model=List[schemas.ReminderResponse], summary="获取当前患者所有提醒", description="获取当前患者的全部提醒列表（用药 + 监测）。")
def get_all_reminders(current_user: models.User = Depends(dependencies.get_current_active_user), db: Session = Depends(dependencies.get_db)):
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return crud.get_all_patient_reminders(db, patient_id=patient.id)

@router.post("/reminders", response_model=schemas.ReminderResponse, summary="添加提醒 (可选关联疾病)", description="添加吃药或复查提醒，可选择是否关联某个慢性病。若未指定，将自动创建一个通用用药分组。")
def add_general_reminder(reminder: schemas.ReminderCreateOptional, current_user: models.User = Depends(dependencies.get_current_active_user), db: Session = Depends(dependencies.get_db)):
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    pd_id = reminder.patient_disease_id
    if pd_id:
        pd = db.query(models.PatientDisease).filter(models.PatientDisease.id == pd_id, models.PatientDisease.patient_id == patient.id).first()
        if not pd:
            raise HTTPException(status_code=404, detail="Disease record not found")
    else:
        from datetime import date as _date
        pd = db.query(models.PatientDisease).filter(
            models.PatientDisease.patient_id == patient.id,
            models.PatientDisease.name == "通用用药"
        ).first()
        if not pd:
            pd = models.PatientDisease(
                patient_id=patient.id,
                name="通用用药",
                status="稳定",
                diagnosis_date=_date.today(),
                last_check_date=_date.today(),
                notes=""
            )
            db.add(pd)
            db.commit()
            db.refresh(pd)
        pd_id = pd.id
    new_reminder = schemas.ReminderCreate(
        patient_disease_id=pd_id,
        type=reminder.type,
        title=reminder.title,
        schedule_text=reminder.schedule_text,
        end_date=reminder.end_date,
        is_active=reminder.is_active
    )
    return crud.create_reminder(db, patient_id=patient.id, reminder=new_reminder)

# --- Revisit Plans ---
@router.get("/revisit-plans", response_model=List[schemas.RevisitPlanResponse], summary="获取复诊计划", description="获取当前患者的所有复诊计划。")
def get_revisit_plans(
    member_id: Optional[UUID4] = None,
    current_user: models.User = Depends(dependencies.get_current_active_user), 
    db: Session = Depends(dependencies.get_db)
):
    """
    获取复诊计划列表
    支持按成员筛选，如未指定则使用当前成员
    """
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    target_member_id = member_id
    if not target_member_id:
        current_member = db.query(models.Member).filter(
            models.Member.patient_id == patient.id,
            models.Member.is_current == True
        ).first()
        if current_member:
            target_member_id = current_member.id
    
    plans = crud.get_patient_revisit_plans(db, patient_id=patient.id)
    
    if target_member_id:
        plans = [p for p in plans if p.member_id == target_member_id]
    else:
        plans = [p for p in plans if p.member_id is None or p.member_id == target_member_id]
    
    return plans

@router.post("/revisit-plans", response_model=schemas.RevisitPlanResponse, summary="创建复诊计划", description="创建新的复诊计划。")
def add_revisit_plan(
    plan: schemas.RevisitPlanCreate, 
    current_user: models.User = Depends(dependencies.get_current_active_user), 
    db: Session = Depends(dependencies.get_db)
):
    """
    创建复诊计划
    自动关联当前成员（如未指定）
    """
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    if not plan.member_id:
        current_member = db.query(models.Member).filter(
            models.Member.patient_id == patient.id,
            models.Member.is_current == True
        ).first()
        if current_member:
            plan.member_id = current_member.id
    
    if plan.patient_disease_id:
        pd = db.query(models.PatientDisease).filter(models.PatientDisease.id == plan.patient_disease_id, models.PatientDisease.patient_id == patient.id).first()
        if not pd:
            raise HTTPException(status_code=404, detail="Disease record not found")
            
    return crud.create_revisit_plan(db, plan=plan, patient_id=patient.id)

@router.put("/revisit-plans/{plan_id}", response_model=schemas.RevisitPlanResponse, summary="更新复诊计划", description="更新复诊计划信息。")
def edit_revisit_plan(plan_id: int, plan_update: schemas.RevisitPlanUpdate, current_user: models.User = Depends(dependencies.get_current_active_user), db: Session = Depends(dependencies.get_db)):
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    updated_plan = crud.update_revisit_plan(db, plan_id=plan_id, plan_update=plan_update, patient_id=patient.id)
    if not updated_plan:
        raise HTTPException(status_code=404, detail="Revisit plan not found")
    return updated_plan

@router.delete("/revisit-plans/{plan_id}", summary="删除复诊计划", description="删除复诊计划。")
def remove_revisit_plan(plan_id: int, current_user: models.User = Depends(dependencies.get_current_active_user), db: Session = Depends(dependencies.get_db)):
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    ok = crud.delete_revisit_plan(db, plan_id=plan_id, patient_id=patient.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Revisit plan not found")
    return {"message": "Successfully deleted"}

# --- Revisit Records ---
@router.post("/revisit-records", response_model=schemas.RevisitRecordResponse, summary="提交复诊记录", description="提交一次复诊记录（打卡），并自动更新关联计划的下次日期。")
def add_revisit_record(
    record: schemas.RevisitRecordCreate, 
    current_user: models.User = Depends(dependencies.get_current_active_user), 
    db: Session = Depends(dependencies.get_db)
):
    """
    提交复诊记录
    自动关联当前成员（如未指定）
    """
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    if not record.member_id:
        current_member = db.query(models.Member).filter(
            models.Member.patient_id == patient.id,
            models.Member.is_current == True
        ).first()
        if current_member:
            record.member_id = current_member.id
        
    return crud.create_revisit_record(db, record=record, patient_id=patient.id)

@router.get("/revisit-records", response_model=List[schemas.RevisitRecordResponse], summary="获取复诊历史", description="获取患者的所有复诊历史记录。")
def get_revisit_records(
    member_id: Optional[UUID4] = None,
    current_user: models.User = Depends(dependencies.get_current_active_user), 
    db: Session = Depends(dependencies.get_db)
):
    """
    获取复诊历史记录
    支持按成员筛选，如未指定则使用当前成员
    """
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    target_member_id = member_id
    if not target_member_id:
        current_member = db.query(models.Member).filter(
            models.Member.patient_id == patient.id,
            models.Member.is_current == True
        ).first()
        if current_member:
            target_member_id = current_member.id
    
    records = crud.get_patient_revisit_records(db, patient_id=patient.id)
    
    if target_member_id:
        records = [r for r in records if r.member_id == target_member_id]
    else:
        records = [r for r in records if r.member_id is None or r.member_id == target_member_id]
    
    return records


@router.get("/medical-records")
def get_medical_records(
    member_id: Optional[UUID4] = None,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    """
    获取病历报告列表
    支持按成员筛选
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    target_member_id = member_id
    if not target_member_id:
        current_member = db.query(models.Member).filter(
            models.Member.patient_id == patient.id,
            models.Member.is_current == True
        ).first()
        if current_member:
            target_member_id = current_member.id
    
    query = db.query(models.Report).filter(
        models.Report.patient_id == patient.id,
        models.Report.report_type == '病历报告'
    )
    
    if target_member_id:
        query = query.filter(models.Report.member_id == target_member_id)
    
    records = query.order_by(models.Report.created_at.desc()).all()
    
    return records


@router.get("/medical-records/{record_id}")
def get_medical_record_detail(
    record_id: UUID4,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    """
    获取病历报告详情
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    record = db.query(models.Report).filter(
        models.Report.id == record_id,
        models.Report.patient_id == patient.id,
        models.Report.report_type == '病历报告'
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    
    return record


@router.delete("/medical-records/{record_id}")
def delete_medical_record(
    record_id: UUID4,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    """
    删除病历报告
    """
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    record = db.query(models.Report).filter(
        models.Report.id == record_id,
        models.Report.patient_id == patient.id,
        models.Report.report_type == '病历报告'
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    
    db.delete(record)
    db.commit()
    
    return {"success": True}


@router.post("/medical-records/upload")
async def upload_medical_record(
    file: UploadFile = File(...),
    member_id: Optional[UUID4] = None,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user)
):
    """
    上传病历报告图片并自动OCR识别
    """
    from ..services import ocr_service
    from ..services.minio_service import minio_service as minio_svc
    from ..config import settings
    import datetime
    
    if current_user.role != models.UserRole.patient:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    patient = crud.get_patient_by_user_id(db, user_id=current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    if not file:
        raise HTTPException(status_code=400, detail="请选择要上传的图片")
    
    content = await file.read()
    
    try:
        bucket = settings.MINIO_BUCKET_REPORT or "jianchabaogao"
        minio_url, object_name = minio_svc.upload_file(
            content, 
            file.filename, 
            file.content_type, 
            bucket_name=bucket
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="上传失败，请重试")
    
    try:
        summary = await ocr_service._run_ocr_job(content, file.filename or "medical_record.jpg")
        medical_fields = ocr_service.extract_medical_fields(summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail="OCR识别失败，请重试")
    
    target_member_id = member_id
    if not target_member_id:
        current_member = db.query(models.Member).filter(
            models.Member.patient_id == patient.id,
            models.Member.is_current == True
        ).first()
        target_member_id = current_member.id if current_member else None
    
    report_date = datetime.date.today()
    if medical_fields.get('report_date'):
        try:
            date_str = medical_fields['report_date']
            date_str = date_str.replace('年', '-').replace('月', '-').replace('日', '')
            report_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            pass
    
    report_data = {
        "ocr_text": summary,
        "category": "medical",
        **medical_fields
    }
    
    report = models.Report(
        patient_id=patient.id,
        member_id=target_member_id,
        report_date=report_date,
        hospital_name=medical_fields.get('hospital', ''),
        report_type='病历报告',
        image_url=minio_url,
        file_name=file.filename,
        status=models.ReportStatus.normal,
        data=report_data,
        summary=summary[:2000] if summary else ""
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return {
        "success": True,
        "report_id": str(report.id),
        "fields": {k: v for k, v in medical_fields.items() if v},
        "message": "上传成功"
    }
