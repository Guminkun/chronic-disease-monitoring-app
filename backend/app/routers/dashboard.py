from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import date, timedelta, datetime
from typing import List, Dict, Any, Optional
from .. import models, dependencies
from ..database import get_db

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"]
)

@router.get("/overview")
def get_dashboard_overview(
    db: Session = Depends(get_db)
):
    """
    获取首页概览数据
    """
    today = date.today()
    month_start = date(today.year, today.month, 1)

    # 1. 基础统计
    total_users = db.query(func.count(models.User.id)).scalar()
    active_users = db.query(func.count(models.User.id)).filter(models.User.is_active == True).scalar()
    
    # 今日复诊 (revisit_records 中 actual_date 为今天，或者 revisit_plans 中 next_date 为今天)
    # 这里简单起见，查计划中 next_date = today 的
    today_revisits = db.query(func.count(models.RevisitPlan.id)).filter(
        models.RevisitPlan.next_date == today,
        models.RevisitPlan.is_active == True
    ).scalar()

    # 待处理报告 (status = normal/warning/critical，尚未被医生查看或处理的逻辑，这里简化为今日上传数)
    # 或者定义为 status = 'pending' 如果有这个状态。目前 status 有 normal, warning, critical。
    # 假设待处理是指今日上传的报告
    pending_reports = db.query(func.count(models.Report.id)).filter(
        models.Report.report_date == today
    ).scalar()

    # 本月新增用户
    new_users_month = db.query(func.count(models.User.id)).filter(
        models.User.created_at >= month_start
    ).scalar()

    # 用药提醒数 (活跃的用药计划数)
    active_med_plans = db.query(func.count(models.MedicationPlan.id)).filter(
        models.MedicationPlan.is_active == True
    ).scalar()

    # 2. 最近用户列表 (取前5个)
    recent_users = db.query(models.Patient).join(models.User).order_by(models.User.created_at.desc()).limit(5).all()
    recent_users_list = []
    for p in recent_users:
        # 获取患者的主要慢性病
        diseases = [d.name for d in p.patient_diseases]
        recent_users_list.append({
            "id": str(p.id),
            "name": p.name,
            "phone": p.user.phone if p.user else "",
            "diseases": diseases,
            "created_at": p.created_at
        })

    # 3. 待处理复诊 (未来7天)
    upcoming_revisits = db.query(models.RevisitPlan).filter(
        models.RevisitPlan.next_date >= today,
        models.RevisitPlan.next_date <= today + timedelta(days=7),
        models.RevisitPlan.is_active == True
    ).order_by(models.RevisitPlan.next_date.asc()).limit(5).all()
    
    revisits_list = []
    for r in upcoming_revisits:
        revisits_list.append({
            "id": r.id,
            "patient_name": r.patient.name,
            "disease_name": r.patient_disease.name if r.patient_disease else "通用",
            "date": r.next_date
        })

    return {
        "stats": {
            "total_users": total_users,
            "active_users": active_users,
            "today_revisits": today_revisits,
            "pending_reports": pending_reports,
            "new_users_month": new_users_month,
            "active_med_plans": active_med_plans
        },
        "recent_users": recent_users_list,
        "upcoming_revisits": revisits_list
    }

@router.get("/trends")
def get_activity_trends(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    获取最近30天用户活跃度趋势
    (这里以每日登录或每日健康数据录入为例)
    """
    today = date.today()
    start_date = today - timedelta(days=days)
    
    # 统计每日健康数据录入量作为活跃度指标
    results = db.query(
        func.date(models.HealthReading.recorded_at).label("date"),
        func.count(models.HealthReading.id).label("count")
    ).filter(
        models.HealthReading.recorded_at >= start_date
    ).group_by(
        func.date(models.HealthReading.recorded_at)
    ).all()
    
    data_map = {str(r.date): r.count for r in results}
    
    trends = []
    for i in range(days):
        day = start_date + timedelta(days=i)
        day_str = str(day)
        trends.append({
            "date": day_str,
            "value": data_map.get(day_str, 0)
        })
        
    return trends


@router.get("/logs")
def get_system_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    action: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(dependencies.get_current_admin)
):
    """获取系统审计日志（管理员专用）"""
    query = db.query(models.SystemLog).join(
        models.User, models.SystemLog.user_id == models.User.id, isouter=True
    )

    if action:
        query = query.filter(models.SystemLog.action == action)
    if q:
        query = query.filter(
            models.SystemLog.action.ilike(f"%{q}%") |
            models.User.phone.ilike(f"%{q}%")
        )

    total = query.count()
    logs = query.order_by(models.SystemLog.created_at.desc()).offset(skip).limit(limit).all()

    action_text_map = {
        "login": "用户登录",
        "create_report": "上传检查报告",
        "delete_report": "删除检查报告",
        "export_data": "导出用户数据",
        "delete_account": "注销账号",
        "create_medication_plan": "创建用药计划",
    }
    action_type_map = {
        "login": ("read", "阅读"),
        "create_report": ("publish", "发布"),
        "delete_report": ("edit", "编辑"),
        "export_data": ("read", "阅读"),
        "delete_account": ("edit", "编辑"),
        "create_medication_plan": ("publish", "发布"),
    }

    items = []
    for log in logs:
        user = db.query(models.User).filter(models.User.id == log.user_id).first() if log.user_id else None
        role_label = {"patient": "患者", "doctor": "医生", "admin": "管理员"}.get(user.role.value if user else "", "用户")
        phone_suffix = user.phone[-4:] if user and user.phone else "----"
        atype, atype_text = action_type_map.get(log.action, ("info", "其他"))

        items.append({
            "time": log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else "",
            "user": f"{role_label} · {phone_suffix}",
            "action": action_text_map.get(log.action, log.action),
            "type": atype,
            "typeText": atype_text,
            "status": "success",
            "ip": log.ip_address or "-",
            "details": log.details,
        })

    return {"total": total, "items": items}
