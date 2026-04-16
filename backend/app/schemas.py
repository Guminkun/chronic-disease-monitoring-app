from pydantic import BaseModel, UUID4, Field, validator, computed_field
from typing import Optional, List, Any, Dict
from datetime import datetime, date
from .models import UserRole, GenderType, DoctorStatus, ReportStatus, BindingStatus, ReminderType

# --- Shared ---
class Token(BaseModel):
    """Token响应模型"""
    access_token: str # 访问令牌
    token_type: str   # 令牌类型 (Bearer)
    role: str         # 用户角色
    user_id: UUID4    # 用户ID

class TokenData(BaseModel):
    """Token载荷数据"""
    phone: Optional[str] = None
    role: Optional[str] = None
    user_id: Optional[UUID4] = None

# --- User ---
class UserBase(BaseModel):
    """用户基础模型"""
    phone: str = Field(..., description="手机号")

class UserCreate(UserBase):
    """用户注册模型"""
    password: str = Field(..., description="密码")
    role: UserRole = Field(..., description="用户角色")

class UserResponse(UserBase):
    """用户响应模型"""
    id: UUID4
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """用户登录模型"""
    phone: str
    password: str

# --- SMS ---
class SMSCodeRequest(BaseModel):
    """发送验证码请求"""
    phone: str = Field(..., description="手机号", min_length=11, max_length=11)

class SMSLoginRequest(BaseModel):
    """短信验证码登录请求"""
    phone: str = Field(..., description="手机号", min_length=11, max_length=11)
    code: str = Field(..., description="验证码", min_length=4, max_length=6)

# --- WeChat ---
class WeChatLoginRequest(BaseModel):
    """微信登录请求"""
    code: str = Field(..., description="微信登录凭证code")
    encrypted_data: Optional[str] = Field(None, description="加密数据")
    iv: Optional[str] = Field(None, description="加密算法初始向量")

class WeChatLoginResponse(BaseModel):
    """微信登录响应"""
    openid: str
    session_key: str
    unionid: Optional[str] = None

 # --- Patient ---
class PatientBase(BaseModel):
    """患者基础模型"""
    name: str = Field(..., description="姓名")
    gender: Optional[GenderType] = Field(None, description="性别")
    age: Optional[int] = Field(None, description="年龄")
    id_card: Optional[str] = Field(None, description="身份证号")
    medical_history: Optional[str] = Field(None, description="既往病史")
    allergies: Optional[str] = Field(None, description="过敏史")

class PatientCreate(PatientBase):
    # 注册时使用，链接到用户
    pass

class PatientUpdate(BaseModel):
    """患者更新模型"""
    medical_history: Optional[str] = Field(None, description="既往病史")
    allergies: Optional[str] = Field(None, description="过敏史")

class PatientResponse(PatientBase):
    """患者信息响应模型"""
    id: UUID4
    user_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

# --- Member ---
class MemberBase(BaseModel):
    """成员基础模型"""
    nickname: str = Field(..., description="昵称", max_length=50)
    relation: str = Field(..., description="关系", max_length=20)

class MemberCreate(MemberBase):
    """成员创建模型"""
    avatar_url: Optional[str] = Field(None, description="头像URL", max_length=500)
    age: Optional[int] = Field(None, description="年龄")
    gender: Optional[GenderType] = Field(None, description="性别")
    height: Optional[float] = Field(None, description="身高(cm)")
    weight: Optional[float] = Field(None, description="体重(kg)")
    blood_type: Optional[str] = Field(None, description="血型", max_length=10)
    lifestyle: Optional[str] = Field(None, description="生活习惯")
    allergy_history: Optional[str] = Field(None, description="过敏史")
    past_history: Optional[str] = Field(None, description="既往病史")
    family_history: Optional[str] = Field(None, description="家族史")
    surgery_history: Optional[str] = Field(None, description="手术史")
    other_notes: Optional[str] = Field(None, description="其他补充")

class MemberUpdate(BaseModel):
    """成员更新模型"""
    nickname: Optional[str] = Field(None, description="昵称", max_length=50)
    relation: Optional[str] = Field(None, description="关系", max_length=20)
    avatar_url: Optional[str] = Field(None, description="头像URL", max_length=500)
    age: Optional[int] = Field(None, description="年龄")
    gender: Optional[GenderType] = Field(None, description="性别")
    height: Optional[float] = Field(None, description="身高(cm)")
    weight: Optional[float] = Field(None, description="体重(kg)")
    blood_type: Optional[str] = Field(None, description="血型", max_length=10)
    lifestyle: Optional[str] = Field(None, description="生活习惯")
    allergy_history: Optional[str] = Field(None, description="过敏史")
    past_history: Optional[str] = Field(None, description="既往病史")
    family_history: Optional[str] = Field(None, description="家族史")
    surgery_history: Optional[str] = Field(None, description="手术史")
    other_notes: Optional[str] = Field(None, description="其他补充")

class MemberResponse(MemberBase):
    """成员信息响应模型"""
    id: UUID4
    patient_id: UUID4
    avatar_url: Optional[str]
    age: Optional[int]
    gender: Optional[GenderType]
    height: Optional[float]
    weight: Optional[float]
    blood_type: Optional[str]
    lifestyle: Optional[str]
    allergy_history: Optional[str]
    past_history: Optional[str]
    family_history: Optional[str]
    surgery_history: Optional[str]
    other_notes: Optional[str]
    is_current: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Doctor ---
class DoctorBase(BaseModel):
    """医生基础模型"""
    name: str = Field(..., description="姓名")
    hospital: Optional[str] = Field(None, description="所属医院")
    department: Optional[str] = Field(None, description="科室")
    license_number: Optional[str] = Field(None, description="执照编号")
    specialties: Optional[List[str]] = Field([], description="擅长领域")
    experience_years: Optional[int] = Field(None, description="从业年限")

class DoctorCreate(DoctorBase):
    pass

class DoctorResponse(DoctorBase):
    """医生信息响应模型"""
    id: UUID4
    user_id: UUID4
    status: DoctorStatus
    rating: float
    rejection_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Disease ---
class DiseaseBase(BaseModel):
    """慢性病基础模型"""
    name: str = Field(..., description="疾病名称 (类目名称)")
    code: Optional[str] = Field(None, description="ICD编码 (类目代码)")
    category: Optional[str] = Field(None, description="原有分类")
    
    # 新增 ICD-10 层级字段
    chapter: Optional[str] = Field(None, description="章")
    chapter_code_range: Optional[str] = Field(None, description="章代码范围")
    chapter_name: Optional[str] = Field(None, description="章名称 (一级分类)")
    section_code_range: Optional[str] = Field(None, description="节代码范围")
    section_name: Optional[str] = Field(None, description="节名称 (二级分类)")
    subcategory_code: Optional[str] = Field(None, description="亚目代码")
    subcategory_name: Optional[str] = Field(None, description="亚目名称")
    diagnosis_code: Optional[str] = Field(None, description="诊断代码")
    diagnosis_name: Optional[str] = Field(None, description="诊断名称")
    
    is_active: bool = Field(True, description="是否启用 (状态)")
    description: Optional[str] = Field(None, description="疾病描述")

class DiseaseCreate(DiseaseBase):
    pass

class DiseaseResponse(DiseaseBase):
    """慢性病响应模型"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class BatchDeleteRequest(BaseModel):
    ids: List[int]

class BatchStatusUpdateRequest(BaseModel):
    ids: List[int]
    is_active: bool

# --- Patient Disease ---
class PatientDiseaseBase(BaseModel):
    """患者慢性病记录基础模型"""
    name: str = Field(..., description="疾病名称")
    status: Optional[str] = Field('active', description="当前状态")
    member_id: Optional[UUID4] = Field(None, description="成员ID")
    diagnosis_date: Optional[date] = Field(None, description="确诊日期")
    last_check_date: Optional[date] = Field(None, description="最后检查日期")
    hospital: Optional[str] = Field(None, description="确诊医院")
    doctor_name: Optional[str] = Field(None, description="主治医生")
    notes: Optional[str] = Field(None, description="备注")

class PatientDiseaseCreate(PatientDiseaseBase):
    pass

class PatientDiseaseUpdate(BaseModel):
    name: Optional[str] = None
    diagnosis_date: Optional[date] = None
    last_check_date: Optional[date] = None
    hospital: Optional[str] = None
    doctor_name: Optional[str] = None
    notes: Optional[str] = None

class PatientDiseaseResponse(PatientDiseaseBase):
    """患者慢性病记录响应模型"""
    id: int
    patient_id: UUID4
    disease_id: Optional[int] = None
    # created_at removed as it does not exist in model

    class Config:
        from_attributes = True

# --- Reminder ---
class ReminderBase(BaseModel):
    """提醒基础模型"""
    type: str = Field(..., description="提醒类型: medication/recheck")
    title: str = Field(..., description="提醒标题")
    schedule_text: Optional[str] = Field(None, description="提醒周期描述")
    end_date: Optional[date] = Field(None, description="截止日期")
    is_active: bool = Field(True, description="是否启用")

class ReminderCreate(ReminderBase):
    patient_disease_id: int

class ReminderCreateOptional(ReminderBase):
    patient_disease_id: Optional[int] = None

class ReminderResponse(ReminderBase):
    """提醒响应模型"""
    id: int
    patient_disease_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Health Report ---
class HealthReportBase(BaseModel):
    """健康日报基础模型"""
    report_date: date = Field(..., description="报告日期")
    mood: Optional[str] = Field(None, description="心情")
    symptoms: Optional[str] = Field(None, description="症状描述")
    measurements: Optional[Dict[str, Any]] = Field(None, description="测量数据(JSON)")

class HealthReportCreate(HealthReportBase):
    pass

class HealthReportResponse(HealthReportBase):
    """健康日报响应模型"""
    id: int
    patient_id: UUID4
    status: ReportStatus
    created_at: datetime

    class Config:
        from_attributes = True

# --- Report (OCR) ---
class ReportMetricBase(BaseModel):
    name: str = Field(..., description="指标名称")
    code: Optional[str] = Field(None, description="指标代码")
    value: str = Field(..., description="数值")
    unit: Optional[str] = Field(None, description="单位")
    reference_range: Optional[str] = Field(None, description="参考范围")
    is_abnormal: bool = Field(False, description="是否异常")
    abnormal_symbol: Optional[str] = Field(None, description="异常符号")

class ReportMetricCreate(ReportMetricBase):
    pass

class ReportMetricResponse(ReportMetricBase):
    id: int
    report_id: UUID4
    report_date: Optional[date] = None # 冗余日期字段，方便前端处理

    class Config:
        from_attributes = True

class MetricTrendPoint(BaseModel):
    """指标趋势点"""
    date: date
    value: float
    unit: Optional[str] = None
    is_abnormal: bool = False

class MetricTrendResponse(BaseModel):
    """指标趋势响应模型"""
    metric_name: str
    unit: Optional[str] = None
    points: List[MetricTrendPoint]

class ReportBase(BaseModel):
    report_date: date = Field(..., description="报告日期")
    hospital_name: Optional[str] = Field(None, description="检查医院")
    report_type: str = Field(..., description="报告类型")
    image_url: Optional[str] = Field(None, description="报告图片URL")
    file_name: Optional[str] = Field(None, description="文件名")
    member_id: Optional[UUID4] = Field(None, description="成员ID")
    patient_disease_id: Optional[int] = Field(None, description="关联疾病ID")
    data: Optional[Any] = Field(None, description="OCR识别原始数据")
    summary: Optional[str] = Field(None, description="报告总结")

class ReportParseResponse(BaseModel):
    """报告解析(OCR)响应模型"""
    report_id: Optional[UUID4] = None
    hospital_name: Optional[str] = None
    report_date: Optional[date] = None
    metrics: List[Dict[str, Any]] = []
    summary: Optional[str] = None
    image_url: Optional[str] = None
    file_name: Optional[str] = None

class ReportUpdate(BaseModel):
    hospital_name: Optional[str] = None
    report_date: Optional[date] = None
    summary: Optional[str] = None
    patient_disease_id: Optional[int] = None
    metrics: Optional[List[ReportMetricCreate]] = None

class ReportCreate(ReportBase):
    patient_id: UUID4 = Field(..., description="患者ID")

class ReportResponse(ReportBase):
    """检查报告响应模型"""
    id: UUID4
    patient_id: UUID4
    status: ReportStatus
    created_at: datetime
    patient_disease: Optional[PatientDiseaseResponse] = None
    metrics: List[ReportMetricResponse] = []

    class Config:
        from_attributes = True

    class Config:
        from_attributes = True

# --- Health Reading ---
class HealthReadingBase(BaseModel):
    """健康指标基础模型"""
    type: str = Field(..., description="指标类型: blood_pressure/blood_sugar/weight")
    value_1: float = Field(..., description="主数值(如收缩压/血糖值/体重)")
    value_2: Optional[float] = Field(None, description="副数值(如舒张压)")
    unit: Optional[str] = Field(None, description="单位")
    notes: Optional[str] = Field(None, description="备注")

class HealthReadingCreate(HealthReadingBase):
    member_id: Optional[UUID4] = Field(None, description="成员ID")

class HealthReadingResponse(HealthReadingBase):
    """健康指标响应模型"""
    id: UUID4
    patient_id: UUID4
    member_id: Optional[UUID4]
    recorded_at: datetime

    class Config:
        from_attributes = True

# --- Indicator ---
class IndicatorBase(BaseModel):
    """指标基础模型"""
    name: str = Field(..., description="指标名称")
    unit: Optional[str] = Field(None, description="单位")
    reference_min: Optional[float] = Field(None, description="参考最小值")
    reference_max: Optional[float] = Field(None, description="参考最大值")
    reference_text: Optional[str] = Field(None, description="参考值描述")
    category: Optional[str] = Field(None, description="分类")

class IndicatorResponse(IndicatorBase):
    """指标响应模型"""
    id: int

    class Config:
        from_attributes = True

# --- Report Type ---
class ReportTypeBase(BaseModel):
    """报告类型基础模型"""
    category: str = Field(..., description="大类")
    name: str = Field(..., description="小类")

class ReportTypeResponse(ReportTypeBase):
    """报告类型响应模型"""
    id: int

    class Config:
        from_attributes = True

class ImagingCheckBase(BaseModel):
    check_id: str
    check_category: str
    check_subcategory: str
    check_part: str
    is_enhanced: int
    applicable_gender: str
    check_desc: Optional[str] = None
    department: str
    sort_num: int

class ImagingCheckResponse(ImagingCheckBase):
    class Config:
        from_attributes = True

# --- Hospital ---
class HospitalBase(BaseModel):
    name: str
    alias: Optional[str] = None
    level: Optional[str] = None
    type: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    website: Optional[str] = None

class HospitalResponse(HospitalBase):
    id: int

    class Config:
        from_attributes = True

# --- Binding ---
class BindingCodeResponse(BaseModel):
    """绑定码响应模型"""
    code: str
    expires_in: int

class BindPatientRequest(BaseModel):
    """绑定患者请求"""
    code: str = Field(..., description="绑定码", min_length=6, max_length=6)

class BindingResponse(BaseModel):
    """绑定关系响应模型"""
    id: UUID4
    doctor_id: UUID4
    patient_id: UUID4
    status: BindingStatus
    created_at: datetime
    
    # Optional nested info
    doctor: Optional[DoctorResponse] = None
    patient: Optional[PatientResponse] = None

    class Config:
        from_attributes = True

# --- Message ---
class MessageBase(BaseModel):
    """消息基础模型"""
    content: str = Field(..., description="消息内容")
    msg_type: str = Field("text", description="消息类型: text/image/voice")

class MessageCreate(MessageBase):
    receiver_id: UUID4 = Field(..., description="接收者ID")

class MessageResponse(MessageBase):
    """消息响应模型"""
    id: int
    sender_id: UUID4
    receiver_id: UUID4
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Revisit Plan ---
class RevisitPlanBase(BaseModel):
    """复诊计划基础模型"""
    patient_disease_id: Optional[int] = Field(None, description="关联疾病ID")
    member_id: Optional[UUID4] = Field(None, description="成员ID")
    cycle_type: str = Field(..., description="周期类型: week/month/quarter/year/custom")
    cycle_value: int = Field(1, description="周期数值")
    next_date: date = Field(..., description="下次复诊日期")
    reminder_days: int = Field(1, description="提前几天提醒")
    notes: Optional[str] = Field(None, description="备注")
    is_active: bool = Field(True, description="是否启用")

class RevisitPlanCreate(RevisitPlanBase):
    pass

class RevisitPlanUpdate(BaseModel):
    cycle_type: Optional[str] = None
    cycle_value: Optional[int] = None
    next_date: Optional[date] = None
    reminder_days: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class RevisitPlanResponse(RevisitPlanBase):
    """复诊计划响应模型"""
    id: int
    patient_id: UUID4
    created_at: datetime
    patient_disease: Optional[PatientDiseaseResponse] = None

    class Config:
        from_attributes = True

# --- Revisit Record ---
class RevisitRecordBase(BaseModel):
    plan_id: Optional[int] = None
    member_id: Optional[UUID4] = Field(None, description="成员ID")
    actual_date: date
    status: str = "completed"
    notes: Optional[str] = None

class RevisitRecordCreate(RevisitRecordBase):
    pass

class RevisitRecordResponse(RevisitRecordBase):
    id: int
    patient_id: UUID4
    created_at: datetime
    plan: Optional[RevisitPlanResponse] = None

    class Config:
        from_attributes = True

# --- Medication Plan ---
class MedicationPlanBase(BaseModel):
    name: str = Field(..., description="药品名称")
    manufacturer: Optional[str] = Field(None, description="生产单位")
    image_url: Optional[str] = None
    member_id: Optional[UUID4] = Field(None, description="成员ID")
    
    dosage_amount: float = Field(..., description="每次剂量")
    dosage_unit: str = Field(..., description="剂量单位")
    
    frequency_type: str = Field(..., description="频率类型: daily/interval/specific_days")
    frequency_value: Optional[str] = Field(None, description="频率值")
    
    taken_times: List[str] = Field(..., description="服药时间列表 HH:MM")
    timing_condition: Optional[str] = Field(None, description="服药时机")
    
    start_date: date = Field(..., description="开始日期")
    end_date: Optional[date] = None
    duration_days: Optional[int] = None
    
    notes: Optional[str] = None
    patient_disease_id: Optional[int] = None
    is_temporary: bool = False
    stock: Optional[float] = None

# --- Notification Center ---
class NotificationBase(BaseModel):
    """通知基础模型"""
    title: str = Field(..., description="通知标题")
    content: str = Field(..., description="通知内容")
    type: str = Field(..., description="通知类型")
    category: str = Field(..., description="通知分类")
    member_id: Optional[UUID4] = Field(None, description="成员ID")
    source_id: Optional[str] = Field(None, description="来源ID")
    source_type: Optional[str] = Field(None, description="来源类型")
    priority: Optional[int] = Field(0, description="优先级")
    extra_data: Optional[dict] = Field(None, description="额外数据")

class NotificationCreate(NotificationBase):
    """创建通知模型"""
    pass

class NotificationUpdate(BaseModel):
    """更新通知模型"""
    is_read: Optional[bool] = None

class NotificationResponse(NotificationBase):
    """通知响应模型"""
    id: int
    patient_id: UUID4
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    member_nickname: Optional[str] = Field(None, description="成员昵称")
    member_relation: Optional[str] = Field(None, description="成员关系")
    
    class Config:
        from_attributes = True

class NotificationListResponse(BaseModel):
    """通知列表响应模型"""
    items: List[NotificationResponse]
    total: int
    unread_count: int

# --- Medication Dictionary ---
class MedicationBase(BaseModel):
    title: Optional[str] = Field(None, description="标题")
    title_url: Optional[str] = Field(None, description="标题链接")
    number: Optional[str] = Field(None, description="编号")
    r3: Optional[str] = Field(None, description="r3")
    generic_name: Optional[str] = Field(None, description="通用名称")
    trade_name: Optional[str] = Field(None, description="商品名称")
    pinyin: Optional[str] = Field(None, description="汉语拼音")
    approval_number: Optional[str] = Field(None, description="批准文号")
    category: Optional[str] = Field(None, description="药品分类")
    manufacturer: Optional[str] = Field(None, description="生产企业")
    drug_nature: Optional[str] = Field(None, description="药品性质")
    related_diseases: Optional[str] = Field(None, description="相关疾病")
    properties: Optional[str] = Field(None, description="性状")
    main_ingredients: Optional[str] = Field(None, description="主要成份")
    indications: Optional[str] = Field(None, description="适应症")
    specification: Optional[str] = Field(None, description="规格")
    adverse_reactions: Optional[str] = Field(None, description="不良反应")
    usage_dosage: Optional[str] = Field(None, description="用法用量")
    contraindications: Optional[str] = Field(None, description="禁忌")
    precautions: Optional[str] = Field(None, description="注意事项")
    pregnancy_lactation: Optional[str] = Field(None, description="孕妇及哺乳期妇女用药")
    pediatric_use: Optional[str] = Field(None, description="儿童用药")
    geriatric_use: Optional[str] = Field(None, description="老人用药")
    drug_interactions: Optional[str] = Field(None, description="药物相互作用")
    pharmacology_toxicology: Optional[str] = Field(None, description="药理毒理")
    pharmacokinetics: Optional[str] = Field(None, description="药代动力学")
    storage: Optional[str] = Field(None, description="贮藏")
    expiry_period: Optional[str] = Field(None, description="有效期")
    therapeutic_system_category: Optional[str] = Field(None, description="治疗系统分类")
    therapeutic_system_subcategory: Optional[str] = Field(None, description="治疗系统二级分类")
    status: str = "active"

class MedicationCreate(MedicationBase):
    pass

class MedicationUpdate(BaseModel):
    title: Optional[str] = None
    title_url: Optional[str] = None
    number: Optional[str] = None
    r3: Optional[str] = None
    generic_name: Optional[str] = None
    trade_name: Optional[str] = None
    pinyin: Optional[str] = None
    approval_number: Optional[str] = None
    category: Optional[str] = None
    manufacturer: Optional[str] = None
    drug_nature: Optional[str] = None
    related_diseases: Optional[str] = None
    properties: Optional[str] = None
    main_ingredients: Optional[str] = None
    indications: Optional[str] = None
    specification: Optional[str] = None
    adverse_reactions: Optional[str] = None
    usage_dosage: Optional[str] = None
    contraindications: Optional[str] = None
    precautions: Optional[str] = None
    pregnancy_lactation: Optional[str] = None
    pediatric_use: Optional[str] = None
    geriatric_use: Optional[str] = None
    drug_interactions: Optional[str] = None
    pharmacology_toxicology: Optional[str] = None
    pharmacokinetics: Optional[str] = None
    storage: Optional[str] = None
    expiry_period: Optional[str] = None
    therapeutic_system_category: Optional[str] = None
    therapeutic_system_subcategory: Optional[str] = None
    status: Optional[str] = None

class MedicationResponse(MedicationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def name(self) -> str:
        return self.generic_name or self.title or ""

    class Config:
        from_attributes = True

# 批量操作请求
class BatchDeleteRequest(BaseModel):
    ids: List[int]

class BatchStatusUpdateRequest(BaseModel):
    ids: List[int]
    is_active: bool

# --- Article ---
class ArticleCategoryBase(BaseModel):
    name: str = Field(..., description="分类名称")
    icon: Optional[str] = Field(None, description="图标URL")
    sort_order: int = Field(0, description="排序权重")
    is_active: bool = True

class ArticleCategoryCreate(ArticleCategoryBase):
    pass

class ArticleCategoryResponse(ArticleCategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ArticleBase(BaseModel):
    title: str = Field(..., description="标题")
    cover_image: Optional[str] = Field(None, description="封面图")
    author: Optional[str] = Field(None, description="作者")
    summary: Optional[str] = Field(None, description="摘要")
    content: Optional[str] = Field(None, description="内容")
    video_url: Optional[str] = Field(None, description="视频地址")
    duration: Optional[str] = Field(None, description="时长")
    is_recommended: bool = False
    is_published: bool = True
    category_id: Optional[int] = None

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    category_id: Optional[int] = None
    cover_image: Optional[str] = None
    author: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[str] = None
    duration: Optional[str] = None
    is_recommended: Optional[bool] = None
    is_published: Optional[bool] = None

class ArticleResponse(ArticleBase):
    id: int
    views: int
    published_at: datetime
    created_at: datetime
    updated_at: datetime
    category: Optional[ArticleCategoryResponse] = None

    class Config:
        from_attributes = True

# --- Patient Dynamic Notifications ---
class PatientNotificationItem(BaseModel):
    id: str = Field(..., description="唯一标识，例如 revisit-1 或 med-2")
    type: str = Field(..., description="通知类型：revisit, medication")
    title: str = Field(..., description="通知标题")
    content: str = Field(..., description="通知内容")
    days_left: int = Field(..., description="剩余天数")
    notification_date: date = Field(..., description="日期")
    member_id: Optional[UUID4] = Field(None, description="成员ID")
    member_nickname: Optional[str] = Field(None, description="成员昵称")
    member_relation: Optional[str] = Field(None, description="成员关系")

class PatientNotificationResponse(BaseModel):
    items: List[PatientNotificationItem]
    count: int

class MedicationPlanCreate(MedicationPlanBase):
    pass

class MedicationPlanUpdate(BaseModel):
    name: Optional[str] = None
    manufacturer: Optional[str] = None
    image_url: Optional[str] = None
    dosage_amount: Optional[float] = None
    dosage_unit: Optional[str] = None
    frequency_type: Optional[str] = None
    frequency_value: Optional[str] = None
    taken_times: Optional[List[str]] = None
    timing_condition: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    stock: Optional[float] = None # 新增

class MedicationPlanResponse(MedicationPlanBase):
    id: int
    patient_id: UUID4
    is_active: bool
    created_at: datetime
    patient_disease: Optional[PatientDiseaseResponse] = None
    
    class Config:
        from_attributes = True

# --- Medication Log ---
class MedicationLogBase(BaseModel):
    plan_id: int
    scheduled_time: datetime
    taken_time: Optional[datetime] = None
    status: str = Field("pending", description="状态: pending/taken/skipped")
    skipped_reason: Optional[str] = None

class MedicationLogCreate(MedicationLogBase):
    pass

class MedicationLogResponse(MedicationLogBase):
    id: int
    patient_id: UUID4
    is_makeup: bool = False
    makeup_reason: Optional[str] = None
    makeup_note: Optional[str] = None
    original_scheduled_time: Optional[datetime] = None
    created_at: datetime
    plan: Optional[MedicationPlanResponse] = None

    class Config:
        from_attributes = True

class MakeupReasonItem(BaseModel):
    """补卡原因选项"""
    value: str
    label: str

class MedicationMakeupCreate(BaseModel):
    """漏服补卡请求"""
    plan_id: int = Field(..., description="用药计划ID")
    scheduled_time: datetime = Field(..., description="原计划用药时间")
    makeup_reason: str = Field(..., description="补卡原因: forgot/discomfort/shortage/other")
    makeup_note: Optional[str] = Field(None, description="补卡备注说明", max_length=500)

class MedicationMakeupResponse(BaseModel):
    """补卡记录响应"""
    id: int
    plan_id: int
    plan_name: str
    scheduled_time: datetime
    taken_time: datetime
    is_makeup: bool = True
    makeup_reason: str
    makeup_note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AvailableMakeupTask(BaseModel):
    """可补卡的漏服任务"""
    plan_id: int
    plan_name: str
    dosage: str
    scheduled_time: datetime
    date_str: str
    is_makeup_done: bool = False

class DailyMedicationTask(BaseModel):
    """每日用药任务视图"""
    plan_id: int
    plan_name: str
    dosage: str # "1 片"
    timing: str # "08:00 饭后"
    scheduled_time: datetime
    log_id: Optional[int] = None
    status: str # pending, taken, skipped
    taken_time: Optional[datetime] = None
    is_temporary: bool = False # 新增

# --- Feedback ---
from .models import FeedbackStatus

class FeedbackBase(BaseModel):
    """意见反馈基础模型"""
    content: str = Field(..., description="反馈内容", min_length=1, max_length=2000)
    images: Optional[List[str]] = Field(None, description="图片URL列表")
    contact: Optional[str] = Field(None, description="联系方式", max_length=100)

class FeedbackCreate(FeedbackBase):
    """创建意见反馈"""
    pass

class FeedbackReply(BaseModel):
    """管理员回复反馈"""
    reply_content: str = Field(..., description="回复内容", min_length=1, max_length=2000)

class FeedbackUpdate(BaseModel):
    """更新反馈状态"""
    status: Optional[str] = Field(None, description="状态: pending/processing/replied/closed")

class FeedbackResponse(BaseModel):
    """意见反馈响应模型"""
    id: int
    user_id: UUID4
    content: str
    images: Optional[List[str]] = None
    contact: Optional[str] = None
    status: FeedbackStatus
    reply_content: Optional[str] = None
    replied_at: Optional[datetime] = None
    replied_by: Optional[UUID4] = None
    created_at: datetime
    updated_at: datetime
    # 用户信息（用于管理端展示）
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    # 回复人信息
    replier_name: Optional[str] = None

    class Config:
        from_attributes = True

class FeedbackListResponse(BaseModel):
    """反馈列表响应"""
    items: List[FeedbackResponse]
    total: int
    page: int
    page_size: int

# --- Usage Guide ---
class UsageGuideBase(BaseModel):
    """使用说明基础模型"""
    title: str = Field(..., description="标题", max_length=200)
    description: Optional[str] = Field(None, description="描述")
    content: Optional[str] = Field(None, description="详细内容")
    cover_image: Optional[str] = Field(None, description="封面图片URL")
    images: Optional[List[str]] = Field(default=[], description="图片URL列表")
    videos: Optional[List[str]] = Field(default=[], description="视频URL列表")
    sort_order: int = Field(0, description="排序权重")
    is_published: bool = Field(True, description="是否发布")

class UsageGuideCreate(UsageGuideBase):
    """创建使用说明"""
    pass

class UsageGuideUpdate(BaseModel):
    """更新使用说明"""
    title: Optional[str] = Field(None, description="标题", max_length=200)
    description: Optional[str] = Field(None, description="描述")
    content: Optional[str] = Field(None, description="详细内容")
    cover_image: Optional[str] = Field(None, description="封面图片URL")
    images: Optional[List[str]] = Field(None, description="图片URL列表")
    videos: Optional[List[str]] = Field(None, description="视频URL列表")
    sort_order: Optional[int] = Field(None, description="排序权重")
    is_published: Optional[bool] = Field(None, description="是否发布")

class UsageGuideResponse(UsageGuideBase):
    """使用说明响应模型"""
    id: int
    views: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UsageGuideListResponse(BaseModel):
    """使用说明列表响应"""
    items: List[UsageGuideResponse]
    total: int
    page: int
    page_size: int
