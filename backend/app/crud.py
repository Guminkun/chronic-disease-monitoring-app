from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Optional
from . import models, schemas, auth_utils
from fastapi import HTTPException, status
import uuid

# --- User ---
def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()

def get_user_by_wechat_openid(db: Session, openid: str):
    return db.query(models.User).filter(models.User.wechat_openid == openid).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth_utils.get_password_hash(user.password)
    db_user = models.User(
        phone=user.phone, 
        password_hash=hashed_password, 
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_wechat_user(db: Session, openid: str, unionid: Optional[str] = None, nickname: Optional[str] = None, avatar: Optional[str] = None, role: models.UserRole = models.UserRole.patient):
    db_user = models.User(
        wechat_openid=openid,
        wechat_unionid=unionid,
        wechat_nickname=nickname,
        wechat_avatar=avatar,
        role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_wechat_user_info(db: Session, user_id: uuid.UUID, openid: str, unionid: Optional[str] = None, nickname: Optional[str] = None, avatar: Optional[str] = None):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.wechat_openid = openid
        if unionid:
            db_user.wechat_unionid = unionid
        if nickname:
            db_user.wechat_nickname = nickname
        if avatar:
            db_user.wechat_avatar = avatar
        db.commit()
        db.refresh(db_user)
    return db_user


# --- Patient ---
def create_patient(db: Session, patient: schemas.PatientCreate, user_id: uuid.UUID):
    db_patient = models.Patient(**patient.model_dump(), user_id=user_id)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def get_patient_by_user_id(db: Session, user_id: uuid.UUID):
    return db.query(models.Patient).filter(models.Patient.user_id == user_id).first()

def get_patient(db: Session, patient_id: uuid.UUID):
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def update_patient(db: Session, patient_id: uuid.UUID, patient_update: schemas.PatientUpdate):
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return None
    
    update_data = patient_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_patient, key, value)
        
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

# --- Doctor ---
def create_doctor(db: Session, doctor: schemas.DoctorCreate, user_id: uuid.UUID):
    db_doctor = models.Doctor(**doctor.model_dump(), user_id=user_id)
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

def get_doctor_by_user_id(db: Session, user_id: uuid.UUID):
    return db.query(models.Doctor).filter(models.Doctor.user_id == user_id).first()

def get_doctors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Doctor).offset(skip).limit(limit).all()

# --- Hospitals ---
def get_hospital(db: Session, hospital_id: int):
    return db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()

def get_hospitals(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Hospital).offset(skip).limit(limit).all()

# --- Diseases ---
def get_diseases(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Disease).offset(skip).limit(limit).all()

def add_patient_disease(db: Session, patient_id: uuid.UUID, disease_data: schemas.PatientDiseaseCreate):
    # Check if disease exists in dictionary to link it (optional)
    disease_id = None
    if disease_data.name:
        disease = db.query(models.Disease).filter(models.Disease.name == disease_data.name).first()
        if disease:
            disease_id = disease.id
    
    # Enforce uniqueness: same patient cannot add same disease twice (by name, case-insensitive)
    existing = (
        db.query(models.PatientDisease)
        .filter(
            models.PatientDisease.patient_id == patient_id,
            func.lower(models.PatientDisease.name) == func.lower(disease_data.name)
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该慢性病已存在，请勿重复添加")

    db_pd = models.PatientDisease(
        patient_id=patient_id, 
        disease_id=disease_id,
        **disease_data.model_dump()
    )
    db.add(db_pd)
    db.commit()
    db.refresh(db_pd)
    return db_pd

def create_doctor_patient_binding(db: Session, doctor_id: uuid.UUID, patient_id: uuid.UUID):
    # Check if binding already exists
    existing = db.query(models.DoctorPatientBinding).filter(
        models.DoctorPatientBinding.doctor_id == doctor_id,
        models.DoctorPatientBinding.patient_id == patient_id
    ).first()
    
    if existing:
        if existing.status != models.BindingStatus.active:
            existing.status = models.BindingStatus.active
            db.commit()
            db.refresh(existing)
        return existing

    # Create new binding
    binding = models.DoctorPatientBinding(
        doctor_id=doctor_id,
        patient_id=patient_id,
        status=models.BindingStatus.active
    )
    db.add(binding)
    db.commit()
    db.refresh(binding)
    return binding

def get_binding(db: Session, doctor_id: uuid.UUID, patient_id: uuid.UUID):
    return db.query(models.DoctorPatientBinding).filter(
        models.DoctorPatientBinding.doctor_id == doctor_id,
        models.DoctorPatientBinding.patient_id == patient_id
    ).first()

def get_doctor_patients(db: Session, doctor_id: uuid.UUID):
    bindings = db.query(models.DoctorPatientBinding).filter(
        models.DoctorPatientBinding.doctor_id == doctor_id,
        models.DoctorPatientBinding.status == models.BindingStatus.active
    ).all()
    # Fetch patient details for each binding (could be optimized with join)
    return bindings 

def get_patient_diseases(db: Session, patient_id: uuid.UUID):
    return db.query(models.PatientDisease).filter(models.PatientDisease.patient_id == patient_id).all()

def update_patient_disease(db: Session, disease_id: int, disease_update: schemas.PatientDiseaseUpdate):
    db_pd = db.query(models.PatientDisease).filter(models.PatientDisease.id == disease_id).first()
    if not db_pd:
        return None
    
    update_data = disease_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_pd, key, value)
        
    db.add(db_pd)
    db.commit()
    db.refresh(db_pd)
    return db_pd

def delete_patient_disease(db: Session, disease_id: int):
    db_pd = db.query(models.PatientDisease).filter(models.PatientDisease.id == disease_id).first()
    if not db_pd:
        return False
    
    db.delete(db_pd)
    db.commit()
    return True

# --- Reports ---
def create_report(db: Session, report: schemas.ReportCreate):
    # Extract metrics if present
    metrics_data = report.metrics
    report_dict = report.model_dump(exclude={"metrics"})
    
    db_report = models.Report(**report_dict)
    db.add(db_report)
    db.flush() # Get report.id before committing
    
    # Save metrics to the new table
    if metrics_data:
        # Ensure the report_metrics table exists even if server wasn't restarted
        try:
            bind = db.get_bind()
            models.ReportMetric.__table__.create(bind=bind, checkfirst=True)
        except Exception:
            pass
        for m in metrics_data:
            db_metric = models.ReportMetric(
                report_id=db_report.id,
                name=m.name,
                code=m.code,
                value=m.value,
                unit=m.unit,
                reference_range=m.reference_range,
                is_abnormal=m.is_abnormal,
                abnormal_symbol=m.abnormal_symbol
            )
            db.add(db_metric)
            
    db.commit()
    db.refresh(db_report)
    return db_report

def get_report(db: Session, report_id: uuid.UUID):
    return (
        db.query(models.Report)
        .options(
            joinedload(models.Report.patient_disease),
            joinedload(models.Report.metrics)
        )
        .filter(models.Report.id == report_id)
        .first()
    )

def get_patient_reports(db: Session, patient_id: uuid.UUID, skip: int = 0, limit: int = 100, with_disease: bool = None):
    query = (
        db.query(models.Report)
        .options(joinedload(models.Report.patient_disease))
        .filter(models.Report.patient_id == patient_id)
    )
    if with_disease is True:
        query = query.filter(models.Report.patient_disease_id.isnot(None))
    elif with_disease is False:
        query = query.filter(models.Report.patient_disease_id.is_(None))
    return (
        query.order_by(models.Report.report_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def delete_report(db: Session, report_id: uuid.UUID):
    db_report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not db_report:
        return False
    
    db.delete(db_report)
    db.commit()
    return True

# --- Health Readings ---
def create_health_reading(db: Session, reading: schemas.HealthReadingCreate, patient_id: uuid.UUID):
    db_reading = models.HealthReading(**reading.model_dump(), patient_id=patient_id)
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading

def get_patient_readings(db: Session, patient_id: uuid.UUID, type: str = None):
    query = db.query(models.HealthReading).filter(models.HealthReading.patient_id == patient_id)
    if type:
        query = query.filter(models.HealthReading.type == type)
    return query.order_by(models.HealthReading.recorded_at.asc()).all()

# --- Bindings ---
def create_binding_request(db: Session, patient_id: uuid.UUID, doctor_id: uuid.UUID):
    db_binding = models.DoctorPatientBinding(
        patient_id=patient_id,
        doctor_id=doctor_id,
        status=models.BindingStatus.pending
    )
    db.add(db_binding)
    db.commit()
    db.refresh(db_binding)
    return db_binding

def get_patient_doctors(db: Session, patient_id: uuid.UUID):
    # Returns bindings with doctor details
    return db.query(models.DoctorPatientBinding).filter(
        models.DoctorPatientBinding.patient_id == patient_id
    ).all()

# --- Chat ---
def create_message(db: Session, message: schemas.MessageCreate, sender_id: uuid.UUID):
    db_message = models.Message(
        sender_id=sender_id,
        receiver_id=message.receiver_id,
        content=message.content,
        msg_type=message.msg_type
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_chat_history(db: Session, user_id_1: uuid.UUID, user_id_2: uuid.UUID, skip: int = 0, limit: int = 50):
    return db.query(models.Message).filter(
        or_(
            (models.Message.sender_id == user_id_1) & (models.Message.receiver_id == user_id_2),
            (models.Message.sender_id == user_id_2) & (models.Message.receiver_id == user_id_1)
        )
    ).order_by(models.Message.created_at.asc()).offset(skip).limit(limit).all()

# --- Reminders ---
def create_reminder(db: Session, patient_id: uuid.UUID, reminder: schemas.ReminderCreate):
    pd = db.query(models.PatientDisease).filter(
        models.PatientDisease.id == reminder.patient_disease_id,
        models.PatientDisease.patient_id == patient_id
    ).first()
    if not pd:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disease record not found")
    db_reminder = models.Reminder(
        patient_id=patient_id,
        patient_disease_id=reminder.patient_disease_id,
        type=reminder.type,
        title=reminder.title,
        schedule_text=reminder.schedule_text,
        end_date=reminder.end_date,
        is_active=reminder.is_active if reminder.is_active is not None else True
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

def get_reminders_by_disease(db: Session, patient_id: uuid.UUID, patient_disease_id: int):
    return db.query(models.Reminder).filter(
        models.Reminder.patient_id == patient_id,
        models.Reminder.patient_disease_id == patient_disease_id
    ).order_by(models.Reminder.created_at.desc()).all()

def get_all_patient_reminders(db: Session, patient_id: uuid.UUID):
    return db.query(models.Reminder).filter(
        models.Reminder.patient_id == patient_id
    ).order_by(models.Reminder.created_at.desc()).all()

def delete_reminder(db: Session, patient_id: uuid.UUID, reminder_id: int):
    db_reminder = db.query(models.Reminder).filter(
        models.Reminder.id == reminder_id,
        models.Reminder.patient_id == patient_id
    ).first()
    if not db_reminder:
        return False
    db.delete(db_reminder)
    db.commit()
    return True

# --- Revisit Plans ---
def create_revisit_plan(db: Session, plan: schemas.RevisitPlanCreate, patient_id: uuid.UUID):
    # Ensure revisit_plans table exists
    try:
        bind = db.get_bind()
        models.RevisitPlan.__table__.create(bind=bind, checkfirst=True)
    except Exception:
        pass

    db_plan = models.RevisitPlan(
        patient_id=patient_id,
        **plan.model_dump()
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def get_patient_revisit_plans(db: Session, patient_id: uuid.UUID):
    return (
        db.query(models.RevisitPlan)
        .options(joinedload(models.RevisitPlan.patient_disease))
        .filter(models.RevisitPlan.patient_id == patient_id)
        .order_by(models.RevisitPlan.next_date.asc())
        .all()
    )

def update_revisit_plan(db: Session, plan_id: int, plan_update: schemas.RevisitPlanUpdate, patient_id: uuid.UUID):
    db_plan = db.query(models.RevisitPlan).filter(
        models.RevisitPlan.id == plan_id,
        models.RevisitPlan.patient_id == patient_id
    ).first()
    
    if not db_plan:
        return None
    
    update_data = plan_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_plan, key, value)
        
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def delete_revisit_plan(db: Session, plan_id: int, patient_id: uuid.UUID):
    db_plan = db.query(models.RevisitPlan).filter(
        models.RevisitPlan.id == plan_id,
        models.RevisitPlan.patient_id == patient_id
    ).first()
    
    if not db_plan:
        return False
    
    db.delete(db_plan)
    db.commit()
    return True

# --- Revisit Records ---
def create_revisit_record(db: Session, record: schemas.RevisitRecordCreate, patient_id: uuid.UUID):
    try:
        bind = db.get_bind()
        models.RevisitRecord.__table__.create(bind=bind, checkfirst=True)
    except Exception:
        pass
    
    db_record = models.RevisitRecord(
        patient_id=patient_id,
        **record.model_dump()
    )
    db.add(db_record)
    
    # If linked to a plan, update the plan's next_date
    if record.plan_id:
        db_plan = db.query(models.RevisitPlan).filter(
            models.RevisitPlan.id == record.plan_id,
            models.RevisitPlan.patient_id == patient_id
        ).first()
        
        if db_plan and record.status == 'completed':
            from datetime import timedelta
            from dateutil.relativedelta import relativedelta
            
            # Calculate next date based on cycle
            current_next = db_plan.next_date
            # Use actual_date as base or current_next? Usually actual_date implies we finished this cycle.
            # Let's base it on the plan's logic to keep cycle consistent, OR base on actual if user wants.
            # Simplest logic: Add cycle to the *current* next_date if it was due.
            # Or better: Add cycle to the actual completion date if it was overdue?
            # Let's use actual_date as the new base for next cycle.
            base_date = record.actual_date
            
            if db_plan.cycle_type == 'week':
                new_date = base_date + timedelta(weeks=db_plan.cycle_value)
            elif db_plan.cycle_type == 'month':
                new_date = base_date + relativedelta(months=db_plan.cycle_value)
            elif db_plan.cycle_type == 'quarter':
                new_date = base_date + relativedelta(months=3 * db_plan.cycle_value)
            elif db_plan.cycle_type == 'year':
                new_date = base_date + relativedelta(years=db_plan.cycle_value)
            elif db_plan.cycle_type == 'custom':
                new_date = base_date + timedelta(days=db_plan.cycle_value)
            else:
                new_date = base_date + relativedelta(months=1) # fallback
                
            db_plan.next_date = new_date
            db.add(db_plan)

    db.commit()
    db.refresh(db_record)
    return db_record

def get_patient_revisit_records(db: Session, patient_id: uuid.UUID):
    return (
        db.query(models.RevisitRecord)
        .options(joinedload(models.RevisitRecord.plan))
        .filter(models.RevisitRecord.patient_id == patient_id)
        .order_by(models.RevisitRecord.actual_date.desc())
        .all()
    )
