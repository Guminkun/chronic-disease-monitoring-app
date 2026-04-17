from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Numeric, Text, ARRAY, JSON, Enum, Uuid, SmallInteger
# from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from .database import Base

# 枚举类型定义
class UserRole(str, enum.Enum):
    patient = "patient" # 患者
    doctor = "doctor"   # 医生
    admin = "admin"     # 管理员

class GenderType(str, enum.Enum):
    male = "male"     # 男
    female = "female" # 女
    other = "other"   # 其他

class DoctorStatus(str, enum.Enum):
    pending = "pending"   # 待审核
    approved = "approved" # 已通过
    rejected = "rejected" # 已拒绝

class ReportStatus(str, enum.Enum):
    normal = "normal"     # 正常
    warning = "warning"   # 警告
    critical = "critical" # 严重

class BindingStatus(str, enum.Enum):
    pending = "pending"   # 申请中
    active = "active"     # 关联中
    rejected = "rejected" # 已拒绝
    unbound = "unbound"   # 已解绑

class ReminderType(str, enum.Enum):
    medication = "medication"
    recheck = "recheck"

# Models

class User(Base):
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    wechat_openid = Column(String(100), unique=True, nullable=True, index=True)
    wechat_unionid = Column(String(100), unique=True, nullable=True, index=True)
    wechat_nickname = Column(String(100), nullable=True)
    wechat_avatar = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    patient = relationship("Patient", back_populates="user", uselist=False)
    doctor = relationship("Doctor", back_populates="user", uselist=False)
    admin = relationship("Admin", back_populates="user", uselist=False)
    system_logs = relationship("SystemLog", back_populates="user")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    gender = Column(Enum(GenderType))
    age = Column(Integer)
    id_card = Column(String(20))
    medical_history = Column(Text) # 既往病史
    allergies = Column(Text) # 过敏史
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="patient")
    patient_diseases = relationship("PatientDisease", back_populates="patient")
    reports = relationship("Report", back_populates="patient")
    health_readings = relationship("HealthReading", back_populates="patient")
    doctor_bindings = relationship("DoctorPatientBinding", back_populates="patient")
    clinical_notes = relationship("ClinicalNote", back_populates="patient")
    reminders = relationship("Reminder", back_populates="patient")
    members = relationship("Member", back_populates="patient", cascade="all, delete-orphan")

class Member(Base):
    """
    成员表
    用于一个账号管理多个成员的健康档案
    """
    __tablename__ = "members"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(Uuid(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    nickname = Column(String(50), nullable=False)
    relation = Column(String(20), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    age = Column(Integer)
    gender = Column(Enum(GenderType))
    height = Column(Numeric(5, 2))
    weight = Column(Numeric(5, 2))
    blood_type = Column(String(10))
    lifestyle = Column(Text)
    allergy_history = Column(Text)
    past_history = Column(Text)
    family_history = Column(Text)
    surgery_history = Column(Text)
    other_notes = Column(Text)
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    patient = relationship("Patient", back_populates="members")

class Doctor(Base):
    """
    医生档案表
    存储医生的执业信息和审核状态
    """
    __tablename__ = "doctors"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String(100), nullable=False) # 姓名
    hospital = Column(String(100)) # 所属医院
    department = Column(String(100)) # 科室
    license_number = Column(String(50)) # 执业证书号
    specialties = Column(JSON) # 擅长领域
    status = Column(Enum(DoctorStatus), default=DoctorStatus.pending) # 审核状态
    rejection_reason = Column(Text) # 拒绝原因
    rating = Column(Numeric(3, 2), default=5.0) # 评分
    experience_years = Column(Integer) # 从业年限
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="doctor")
    reports = relationship("Report", back_populates="doctor")
    patient_bindings = relationship("DoctorPatientBinding", back_populates="doctor")
    clinical_notes = relationship("ClinicalNote", back_populates="doctor")

class Admin(Base):
    """
    管理员表
    """
    __tablename__ = "admins"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    role_level = Column(String(50), default="admin")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="admin")

class Disease(Base):
    """
    慢性病字典表
    系统支持的慢性病类型定义
    """
    __tablename__ = "diseases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False) # 疾病名称 (对应 类目名称)
    code = Column(String(50)) # ICD编码 (对应 类目代码)
    category = Column(String(100)) # 原有分类字段 (建议保留以兼容旧数据)
    
    # 新增 ICD-10 层级字段
    chapter = Column(String(50)) # 章
    chapter_code_range = Column(String(100)) # 章代码范围
    chapter_name = Column(String(200)) # 章的名称 (Web: 一级分类)
    section_code_range = Column(String(100)) # 节代码范围
    section_name = Column(String(200)) # 节名称 (Web: 二级分类)
    subcategory_code = Column(String(50)) # 亚目代码
    subcategory_name = Column(String(200)) # 亚目名称
    diagnosis_code = Column(String(50)) # 诊断代码
    diagnosis_name = Column(String(200)) # 诊断名称
    
    is_active = Column(Boolean, default=True) # 是否启用 (状态)
    description = Column(Text) # 描述
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient_diseases = relationship("PatientDisease", back_populates="disease")
    disease_indicators = relationship("DiseaseIndicator", back_populates="disease")

class PatientDisease(Base):
    """
    患者疾病关联表
    记录患者确诊的慢性病
    """
    __tablename__ = "patient_diseases"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Uuid(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Uuid(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), nullable=True)
    disease_id = Column(Integer, ForeignKey("diseases.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(100), nullable=False)
    diagnosis_date = Column(Date)
    last_check_date = Column(Date)
    hospital = Column(String(100))
    doctor_name = Column(String(50))
    notes = Column(Text)
    status = Column(String(50), default="active")

    patient = relationship("Patient", back_populates="patient_diseases")
    member = relationship("Member")
    disease = relationship("Disease", back_populates="patient_diseases")
    reminders = relationship("Reminder", back_populates="patient_disease")

class Indicator(Base):
    """
    健康指标字典表
    定义可测量的健康指标（如血压、血糖）
    """
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False) # 指标名称
    abbreviation = Column(String(50)) # 英文缩写
    unit = Column(String(20)) # 单位
    reference_min = Column(Numeric) # 参考最小值
    reference_max = Column(Numeric) # 参考最大值
    reference_text = Column(String(100)) # 参考值描述（用于非数值或复杂范围）
    category = Column(String(50)) # 分类
    clinical_significance = Column(Text) # 临床意义

    disease_indicators = relationship("DiseaseIndicator", back_populates="indicator")

class DiseaseIndicator(Base):
    """
    疾病-指标关联表
    定义某种疾病需要关注哪些指标
    """
    __tablename__ = "disease_indicators"

    disease_id = Column(Integer, ForeignKey("diseases.id", ondelete="CASCADE"), primary_key=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id", ondelete="CASCADE"), primary_key=True)
    is_required = Column(Boolean, default=False) # 是否必测

    disease = relationship("Disease", back_populates="disease_indicators")
    indicator = relationship("Indicator", back_populates="disease_indicators")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(Uuid(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Uuid(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), nullable=True)
    doctor_id = Column(Uuid(as_uuid=True), ForeignKey("doctors.id", ondelete="SET NULL"))
    report_date = Column(Date, nullable=False)
    hospital_name = Column(String(100))
    report_type = Column(String(50), nullable=False)
    image_url = Column(Text)  # File key path (e.g., user_xxx/member_xxx/reports/xxx.jpg)
    thumbnail_url = Column(Text, nullable=True)  # Thumbnail file key path
    file_name = Column(String(255))
    file_md5 = Column(String(32), nullable=True)  # MD5 hash for deduplication
    patient_disease_id = Column(Integer, ForeignKey("patient_diseases.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(ReportStatus), default=ReportStatus.normal)
    data = Column(JSON)
    summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="reports")
    member = relationship("Member")
    doctor = relationship("Doctor", back_populates="reports")
    patient_disease = relationship("PatientDisease")
    metrics = relationship("ReportMetric", back_populates="report", cascade="all, delete-orphan")

class ReportMetric(Base):
    """
    检查报告指标明细表
    存储 OCR 识别并经用户确认的各项指标数据
    """
    __tablename__ = "report_metrics"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Uuid(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False) # 指标名称 (如：白细胞计数)
    code = Column(String(50)) # 指标代码 (如：WBC)
    value = Column(String(50), nullable=False) # 测量值
    unit = Column(String(50)) # 单位
    reference_range = Column(String(100)) # 参考范围
    is_abnormal = Column(Boolean, default=False) # 是否异常
    abnormal_symbol = Column(String(10)) # 异常符号 (↑, ↓)

    report = relationship("Report", back_populates="metrics")

class HealthReading(Base):
    __tablename__ = "health_readings"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(Uuid(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Uuid(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), nullable=True)
    type = Column(String(50), nullable=False)
    value_1 = Column(Numeric, nullable=False)
    value_2 = Column(Numeric)
    unit = Column(String(20))
    notes = Column(Text)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="health_readings")
    member = relationship("Member")

class Message(Base):
    """
    聊天消息表
    """
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    receiver_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    msg_type = Column(String(20), default="text") # text, image
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="received_messages")

class DoctorPatientBinding(Base):
    __tablename__ = "doctor_patient_bindings"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(Uuid(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(Uuid(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(BindingStatus), default=BindingStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    doctor = relationship("Doctor", back_populates="patient_bindings")
    patient = relationship("Patient", back_populates="doctor_bindings")

class ClinicalNote(Base):
    __tablename__ = "clinical_notes"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(Uuid(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(Uuid(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    doctor = relationship("Doctor", back_populates="clinical_notes")
    patient = relationship("Patient", back_populates="clinical_notes")

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Uuid(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Uuid(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), nullable=True)
    patient_disease_id = Column(Integer, ForeignKey("patient_diseases.id", ondelete="CASCADE"), nullable=True)
    type = Column(Enum(ReminderType), nullable=False)
    title = Column(String(200), nullable=False)
    schedule_text = Column(String(200))
    end_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="reminders")
    member = relationship("Member")
    patient_disease = relationship("PatientDisease", back_populates="reminders")

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(100), nullable=False)
    resource = Column(String(100))
    details = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="system_logs")

class ReportType(Base):
    """
    报告类型字典表
    """
    __tablename__ = "report_types"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False) # 大类
    name = Column(String(100), nullable=False) # 小类

class HospitalImagingCheck(Base):
    __tablename__ = "hospital_imaging_check"

    check_id = Column(String(32), primary_key=True)
    check_category = Column(String(20), nullable=False)
    check_subcategory = Column(String(50), nullable=False)
    check_part = Column(String(30), nullable=False)
    is_enhanced = Column(SmallInteger, nullable=False, default=0)
    applicable_gender = Column(String(10), nullable=False, default="通用")
    check_desc = Column(String(200), nullable=False, default="")
    department = Column(String(20), nullable=False)
    sort_num = Column(Integer, nullable=False, default=0)

class Hospital(Base):
    """
    医院信息表
    """
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    alias = Column(String(200))
    level = Column(String(50))
    type = Column(String(100))
    address = Column(String(500))
    phone = Column(String(100))
    province = Column(String(50))
    city = Column(String(50))
    district = Column(String(50))
    website = Column(String(200))
    founded_year = Column(String(20))
    president = Column(String(100))
    management_type = Column(String(50))
    is_medical_insurance = Column(String(20))
    bed_count = Column(String(50))
    annual_outpatient = Column(String(50))
    staff_count = Column(String(50))
    departments = Column(Text)
    email = Column(String(200))
    postcode = Column(String(20))
    introduction = Column(Text)

class Notification(Base):
    """
    通知中心表
    统一管理所有成员的所有类型通知
    """
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Uuid(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Uuid(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), nullable=True)
    
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    
    source_id = Column(String(100))
    source_type = Column(String(50))
    
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))
    
    is_handled = Column(Boolean, default=False)
    handled_at = Column(DateTime(timezone=True))
    handler_type = Column(String(50))
    
    priority = Column(Integer, default=0)
    extra_data = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    patient = relationship("Patient")
    member = relationship("Member")

class RevisitPlan(Base):
    """
    复诊计划表
    记录患者的复诊计划和周期
    """
    __tablename__ = "revisit_plans"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Uuid(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Uuid(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), nullable=True)
    patient_disease_id = Column(Integer, ForeignKey("patient_diseases.id", ondelete="CASCADE"), nullable=True)
    cycle_type = Column(String(50), nullable=False)
    cycle_value = Column(Integer, default=1)
    next_date = Column(Date, nullable=False)
    reminder_days = Column(Integer, default=1)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", backref="revisit_plans")
    member = relationship("Member")
    patient_disease = relationship("PatientDisease")

class RevisitRecord(Base):
    """
    复诊历史记录表
    记录每次实际复诊的情况
    """
    __tablename__ = "revisit_records"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("revisit_plans.id", ondelete="SET NULL"), nullable=True)
    patient_id = Column(Uuid(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Uuid(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), nullable=True)
    actual_date = Column(Date, nullable=False)
    status = Column(String(50), default="completed")
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    plan = relationship("RevisitPlan", backref="records")
    patient = relationship("Patient", backref="revisit_records")

class MedicationPlan(Base):
    """
    用药计划表
    """
    __tablename__ = "medication_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Uuid(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Uuid(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), nullable=True)
    patient_disease_id = Column(Integer, ForeignKey("patient_diseases.id", ondelete="SET NULL"), nullable=True)
    
    name = Column(String(200), nullable=False)
    manufacturer = Column(String(200), nullable=True)
    image_url = Column(String(500), nullable=True)
    
    dosage_amount = Column(Numeric(10, 2), nullable=False, default=1)
    dosage_unit = Column(String(20), nullable=False, default="片")
    
    frequency_type = Column(String(50), nullable=False, default="daily")
    frequency_value = Column(String(50), nullable=True)
    
    taken_times = Column(JSON, nullable=False)
    timing_condition = Column(String(50), nullable=True)
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    duration_days = Column(Integer, nullable=True)
    
    is_active = Column(Boolean, default=True)
    is_temporary = Column(Boolean, default=False)
    paused_until = Column(Date, nullable=True)
    stock = Column(Numeric(10, 2), nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    patient = relationship("Patient", backref="medication_plans")
    member = relationship("Member")
    patient_disease = relationship("PatientDisease")
    logs = relationship("MedicationLog", back_populates="plan", cascade="all, delete-orphan")

class MedicationLog(Base):
    """
    用药打卡记录表
    """
    __tablename__ = "medication_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("medication_plans.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(Uuid(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    member_id = Column(Uuid(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), nullable=True)
    
    scheduled_time = Column(DateTime, nullable=False) # 计划服药时间
    taken_time = Column(DateTime, nullable=True) # 实际服药时间
    
    status = Column(String(20), default="pending") # pending, taken, skipped
    skipped_reason = Column(String(200), nullable=True)
    
    is_makeup = Column(Boolean, default=False) # 是否为补卡记录
    makeup_reason = Column(String(50), nullable=True) # 补卡原因: forgot/discomfort/shortage/other
    makeup_note = Column(String(500), nullable=True) # 补卡备注说明
    original_scheduled_time = Column(DateTime, nullable=True) # 原计划用药时间(补卡时记录)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    plan = relationship("MedicationPlan", back_populates="logs")
    patient = relationship("Patient")
    member = relationship("Member")

class ArticleCategory(Base):
    """
    健康宣教文章分类表
    """
    __tablename__ = "article_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True) # 分类名称 (如：糖尿病、高血压、饮食指导)
    icon = Column(String(500)) # 分类图标URL
    sort_order = Column(Integer, default=0) # 排序权重
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    articles = relationship("Article", back_populates="category")

class Article(Base):
    """
    健康宣教文章表
    """
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("article_categories.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200), nullable=False) # 标题
    cover_image = Column(String(500)) # 封面图
    author = Column(String(100)) # 作者/来源
    summary = Column(Text) # 摘要
    content = Column(Text) # 内容 (HTML/Markdown)
    video_url = Column(String(500)) # 视频地址 (可选)
    duration = Column(String(50)) # 阅读时长/视频时长 (如 "5分钟")
    views = Column(Integer, default=0) # 浏览量
    is_recommended = Column(Boolean, default=False) # 是否推荐
    is_published = Column(Boolean, default=True) # 是否发布
    published_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category = relationship("ArticleCategory", back_populates="articles")

class Medication(Base):
    """
    药品基础字典表
    """
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300))                         # 标题
    title_url = Column(String(500))                     # 标题链接
    number = Column(String(100))                        # 编号
    r3 = Column(String(200))                            # r3
    generic_name = Column(String(200), index=True)      # 通用名称
    trade_name = Column(String(200))                    # 商品名称
    pinyin = Column(String(300))                        # 汉语拼音
    approval_number = Column(String(100))               # 批准文号
    category = Column(String(100))                      # 药品分类
    manufacturer = Column(String(200))                  # 生产企业
    drug_nature = Column(String(100))                   # 药品性质
    related_diseases = Column(Text)                     # 相关疾病
    properties = Column(Text)                           # 性状
    main_ingredients = Column(Text)                     # 主要成份
    indications = Column(Text)                          # 适应症
    specification = Column(String(200))                 # 规格
    adverse_reactions = Column(Text)                    # 不良反应
    usage_dosage = Column(Text)                         # 用法用量
    contraindications = Column(Text)                    # 禁忌
    precautions = Column(Text)                          # 注意事项
    pregnancy_lactation = Column(Text)                  # 孕妇及哺乳期妇女用药
    pediatric_use = Column(Text)                        # 儿童用药
    geriatric_use = Column(Text)                        # 老人用药
    drug_interactions = Column(Text)                    # 药物相互作用
    pharmacology_toxicology = Column(Text)              # 药理毒理
    pharmacokinetics = Column(Text)                     # 药代动力学
    storage = Column(Text)                              # 贮藏
    expiry_period = Column(String(200))                 # 有效期
    therapeutic_system_category = Column(String(100))   # 治疗系统分类
    therapeutic_system_subcategory = Column(String(100))# 治疗系统二级分类

    status = Column(String(50), default="active")       # active, inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class FeedbackStatus(str, enum.Enum):
    """反馈状态枚举"""
    pending = "pending"       # 待处理
    processing = "processing" # 处理中
    replied = "replied"       # 已回复
    closed = "closed"         # 已关闭

class Feedback(Base):
    """
    用户意见反馈表
    """
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)                    # 反馈内容
    images = Column(JSON, nullable=True)                      # 图片URL列表
    contact = Column(String(100), nullable=True)              # 联系方式（可选）
    status = Column(Enum(FeedbackStatus), default=FeedbackStatus.pending)  # 处理状态
    reply_content = Column(Text, nullable=True)               # 回复内容
    replied_at = Column(DateTime(timezone=True), nullable=True)  # 回复时间
    replied_by = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # 回复人
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", foreign_keys=[user_id], backref="feedbacks")
    replier = relationship("User", foreign_keys=[replied_by])

class UsageGuide(Base):
    """
    使用说明表
    存储小程序功能使用说明内容，包括文本、图片和视频
    """
    __tablename__ = "usage_guides"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)              # 标题
    description = Column(Text)                                # 描述
    content = Column(Text)                                    # 详细内容 (富文本/Markdown)
    cover_image = Column(String(500))                         # 封面图片URL (MinIO)
    images = Column(JSON, default=list)                       # 图片URL列表 (MinIO)
    videos = Column(JSON, default=list)                       # 视频URL列表 (MinIO)
    sort_order = Column(Integer, default=0)                   # 排序权重
    is_published = Column(Boolean, default=True)              # 是否发布
    views = Column(Integer, default=0)                        # 浏览量
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class WechatSubscription(Base):
    """
    微信订阅消息授权表
    记录用户在小程序端授权订阅消息的状态
    """
    __tablename__ = "wechat_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    openid = Column(String(100), nullable=False, index=True)
    template_id = Column(String(100), nullable=False)
    
    is_subscribed = Column(Boolean, default=True)
    subscribe_count = Column(Integer, default=0)
    used_count = Column(Integer, default=0)
    
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", backref="wechat_subscriptions")
