from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional, List
from uuid import UUID
from .. import models

class NotificationService:
    @staticmethod
    def create_notification(
        db: Session,
        patient_id: UUID,
        member_id: Optional[UUID],
        title: str,
        content: str,
        type: str,
        category: str,
        source_id: Optional[str] = None,
        source_type: Optional[str] = None,
        priority: int = 0,
        extra_data: Optional[dict] = None
    ) -> models.Notification:
        notification = models.Notification(
            patient_id=patient_id,
            member_id=member_id,
            title=title,
            content=content,
            type=type,
            category=category,
            source_id=source_id,
            source_type=source_type,
            priority=priority,
            extra_data=extra_data
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def generate_revisit_reminders(db: Session, patient_id: Optional[UUID] = None):
        today = date.today()
        remind_before_days = 7
        
        query = db.query(models.RevisitPlan).filter(
            models.RevisitPlan.is_active == True,
            models.RevisitPlan.next_date >= today,
            models.RevisitPlan.next_date <= today + timedelta(days=remind_before_days)
        )
        
        if patient_id:
            query = query.filter(models.RevisitPlan.patient_id == patient_id)
        
        plans = query.all()
        notifications = []
        
        for plan in plans:
            days_left = (plan.next_date - today).days
            disease_name = plan.patient_disease.name if plan.patient_disease else "通用"
            
            existing = db.query(models.Notification).filter(
                models.Notification.source_type == "revisit_plan",
                models.Notification.source_id == str(plan.id),
                models.Notification.created_at >= today
            ).first()
            
            if existing:
                continue
            
            notification = NotificationService.create_notification(
                db=db,
                patient_id=plan.patient_id,
                member_id=plan.member_id,
                title="复诊提醒",
                content=f"您的{disease_name}复诊计划即将在 {plan.next_date} 进行，还有 {days_left} 天。",
                type="revisit",
                category="health",
                source_id=str(plan.id),
                source_type="revisit_plan",
                priority=10 if days_left <= 3 else 5
            )
            notifications.append(notification)
        
        return notifications

    @staticmethod
    def generate_medication_reminders(db: Session, patient_id: Optional[UUID] = None):
        today = date.today()
        remind_before_days = 3
        
        query = db.query(models.MedicationPlan).filter(
            models.MedicationPlan.is_active == True,
            models.MedicationPlan.end_date != None,
            models.MedicationPlan.end_date >= today,
            models.MedicationPlan.end_date <= today + timedelta(days=remind_before_days)
        )
        
        if patient_id:
            query = query.filter(models.MedicationPlan.patient_id == patient_id)
        
        plans = query.all()
        notifications = []
        
        for plan in plans:
            if not plan.end_date:
                continue
            days_left = (plan.end_date - today).days
            
            existing = db.query(models.Notification).filter(
                models.Notification.source_type == "medication_plan",
                models.Notification.source_id == str(plan.id),
                models.Notification.created_at >= today
            ).first()
            
            if existing:
                continue
            
            notification = NotificationService.create_notification(
                db=db,
                patient_id=plan.patient_id,
                member_id=plan.member_id,
                title="药品余量不足",
                content=f"您的药品 {plan.name} 余量即将用完（截止日期 {plan.end_date}），请及时补充。还有 {days_left} 天用量。",
                type="medication",
                category="health",
                source_id=str(plan.id),
                source_type="medication_plan",
                priority=8 if days_left <= 1 else 4
            )
            notifications.append(notification)
        
        return notifications

    @staticmethod
    def generate_all_reminders(db: Session, patient_id: Optional[UUID] = None):
        revisit_notis = NotificationService.generate_revisit_reminders(db, patient_id)
        medication_notis = NotificationService.generate_medication_reminders(db, patient_id)
        return revisit_notis + medication_notis

notification_service = NotificationService()
