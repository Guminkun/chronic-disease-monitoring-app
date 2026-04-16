from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from .. import crud, schemas, models, dependencies
from ..binding_manager import manager as binding_manager

router = APIRouter(
    prefix="/doctors",
    tags=["doctors"],
)

@router.post("/patients/bind", response_model=schemas.BindingResponse, summary="绑定患者", description="医生通过输入患者生成的绑定码建立绑定关系。")
def bind_patient(
    bind_req: schemas.BindPatientRequest,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    """
    绑定患者
    """
    if current_user.role != models.UserRole.doctor:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    doctor = crud.get_doctor_by_user_id(db, user_id=current_user.id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
        
    # Verify code
    patient_id = binding_manager.verify_code(bind_req.code)
    if not patient_id:
        raise HTTPException(status_code=400, detail="Invalid or expired binding code")
        
    # Create binding
    return crud.create_doctor_patient_binding(db, doctor_id=doctor.id, patient_id=patient_id)

@router.get("/me", response_model=schemas.DoctorResponse, summary="获取当前医生信息", description="获取当前登录医生的个人详细档案。")
def read_doctor_me(current_user: models.User = Depends(dependencies.get_current_active_user), db: Session = Depends(dependencies.get_db)):
    """
    获取医生个人信息
    需要医生权限
    """
    # 验证用户角色
    if current_user.role != models.UserRole.doctor:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # 查询医生档案
    doctor = crud.get_doctor_by_user_id(db, user_id=current_user.id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    return doctor

@router.get("/", response_model=List[schemas.DoctorResponse], summary="获取医生列表", description="分页获取系统中的所有医生列表。")
def read_doctors(skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db)):
    """
    获取医生列表（分页）
    :param skip: 跳过数量
    :param limit: 返回数量限制
    """
    return crud.get_doctors(db, skip=skip, limit=limit)

@router.get("/patients", response_model=List[schemas.BindingResponse], summary="获取我的患者", description="获取当前医生绑定的所有患者列表。")
def get_my_patients(current_user: models.User = Depends(dependencies.get_current_active_user), db: Session = Depends(dependencies.get_db)):
    """
    获取我的患者列表
    """
    if current_user.role != models.UserRole.doctor:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    doctor = crud.get_doctor_by_user_id(db, user_id=current_user.id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
        
    return crud.get_doctor_patients(db, doctor_id=doctor.id)

@router.get("/patients/{patient_id}/readings", response_model=List[schemas.HealthReadingResponse], summary="获取患者健康数据", description="获取指定患者的健康数据记录。")
def get_patient_readings(
    patient_id: uuid.UUID,
    type: Optional[str] = None,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    """
    获取患者健康数据
    需要医生权限，且该医生与患者存在绑定关系
    """
    if current_user.role != models.UserRole.doctor:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    doctor = crud.get_doctor_by_user_id(db, user_id=current_user.id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
        
    # Check binding
    binding = crud.get_binding(db, doctor_id=doctor.id, patient_id=patient_id)
    if not binding:
        raise HTTPException(status_code=403, detail="Patient not bound to this doctor")
        
    return crud.get_patient_readings(db, patient_id=patient_id, type=type)

@router.get("/patients/{patient_id}/diseases", response_model=List[schemas.PatientDiseaseResponse], summary="获取患者慢性病", description="获取指定患者的慢性病列表。")
def get_patient_diseases(
    patient_id: uuid.UUID,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    if current_user.role != models.UserRole.doctor:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    doctor = crud.get_doctor_by_user_id(db, user_id=current_user.id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
        
    binding = crud.get_binding(db, doctor_id=doctor.id, patient_id=patient_id)
    if not binding:
        raise HTTPException(status_code=403, detail="Patient not bound to this doctor")
        
    return crud.get_patient_diseases(db, patient_id=patient_id)

@router.get("/patients/{patient_id}/reports", response_model=List[schemas.ReportResponse], summary="获取患者报告", description="获取指定患者的检查报告列表。")
def get_patient_reports(
    patient_id: uuid.UUID,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    if current_user.role != models.UserRole.doctor:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    doctor = crud.get_doctor_by_user_id(db, user_id=current_user.id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
        
    binding = crud.get_binding(db, doctor_id=doctor.id, patient_id=patient_id)
    if not binding:
        raise HTTPException(status_code=403, detail="Patient not bound to this doctor")
        
    return crud.get_patient_reports(db, patient_id=patient_id)

@router.get("/patients/{patient_id}/reminders", response_model=List[schemas.ReminderResponse], summary="获取患者提醒", description="获取指定患者的所有提醒（用药/复查）。")
def get_patient_reminders(
    patient_id: uuid.UUID,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    if current_user.role != models.UserRole.doctor:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    doctor = crud.get_doctor_by_user_id(db, user_id=current_user.id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
        
    binding = crud.get_binding(db, doctor_id=doctor.id, patient_id=patient_id)
    if not binding:
        raise HTTPException(status_code=403, detail="Patient not bound to this doctor")
        
    return crud.get_all_patient_reminders(db, patient_id=patient_id)

@router.get("/patients/{patient_id}", response_model=schemas.PatientResponse, summary="获取患者详情", description="获取指定患者的详细档案信息。")
def get_patient_detail(
    patient_id: uuid.UUID,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    """
    获取患者详细档案
    需要医生权限，且该医生与患者存在绑定关系
    """
    if current_user.role != models.UserRole.doctor:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    doctor = crud.get_doctor_by_user_id(db, user_id=current_user.id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
        
    # Check binding
    binding = crud.get_binding(db, doctor_id=doctor.id, patient_id=patient_id)
    if not binding:
        raise HTTPException(status_code=403, detail="Patient not bound to this doctor")
        
    patient = crud.get_patient(db, patient_id=patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    return patient

@router.put("/patients/{patient_id}", response_model=schemas.PatientResponse, summary="更新患者档案", description="更新指定患者的既往病史和过敏史等信息。")
def update_patient_detail(
    patient_id: uuid.UUID,
    patient_update: schemas.PatientUpdate,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db)
):
    """
    更新患者档案（仅限医生）
    需要医生权限，且该医生与患者存在绑定关系
    """
    if current_user.role != models.UserRole.doctor:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    doctor = crud.get_doctor_by_user_id(db, user_id=current_user.id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
        
    # Check binding
    binding = crud.get_binding(db, doctor_id=doctor.id, patient_id=patient_id)
    if not binding:
        raise HTTPException(status_code=403, detail="Patient not bound to this doctor")
        
    patient = crud.update_patient(db, patient_id=patient_id, patient_update=patient_update)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    return patient
