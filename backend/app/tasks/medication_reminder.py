import asyncio
from datetime import datetime, date, timedelta
from typing import List
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import MedicationPlan, MedicationLog, User, WechatSubscription
from ..services.wechat_service import wechat_service
from ..logging_config import get_logger

logger = get_logger(__name__)

def get_medication_tasks_for_reminder(db: Session, reminder_time: datetime) -> List[dict]:
    now = datetime.now()
    today = now.date()
    
    reminder_window_start = now - timedelta(minutes=2)
    reminder_window_end = now + timedelta(minutes=2)
    
    plans = db.query(MedicationPlan).filter(
        MedicationPlan.is_active == True,
        MedicationPlan.start_date <= today,
    ).all()
    
    tasks = []
    
    for plan in plans:
        if plan.paused_until and plan.paused_until >= today:
            continue
        
        if plan.end_date and plan.end_date < today:
            continue
        
        is_due = False
        if plan.frequency_type == "daily":
            is_due = True
        elif plan.frequency_type == "interval":
            try:
                interval = int(plan.frequency_value or 1)
                days_diff = (today - plan.start_date).days
                if days_diff >= 0 and days_diff % (interval + 1) == 0:
                    is_due = True
            except:
                pass
        elif plan.frequency_type == "specific_days":
            try:
                weekday = today.weekday() + 1
                if str(weekday) in (plan.frequency_value or "").split(","):
                    is_due = True
            except:
                pass
        
        if not is_due:
            continue
        
        for take_time in (plan.taken_times or []):
            try:
                hour, minute = map(int, take_time.split(":"))
                scheduled_time = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
                
                if reminder_window_start <= scheduled_time <= reminder_window_end:
                    existing_log = db.query(MedicationLog).filter(
                        MedicationLog.plan_id == plan.id,
                        MedicationLog.scheduled_time == scheduled_time
                    ).first()
                    
                    if existing_log:
                        continue
                    
                    tasks.append({
                        "plan": plan,
                        "scheduled_time": scheduled_time,
                        "take_time": take_time
                    })
            except Exception as e:
                logger.error(f"Error parsing take_time {take_time}: {e}")
                continue
    
    return tasks

async def send_medication_reminders():
    db = SessionLocal()
    try:
        tasks = get_medication_tasks_for_reminder(db, datetime.now())
        
        for task in tasks:
            plan = task["plan"]
            scheduled_time = task["scheduled_time"]
            
            user = db.query(User).filter(User.id == plan.patient.user_id).first()
            if not user or not user.wechat_openid:
                logger.debug(f"User not found or no openid for plan {plan.id}")
                continue
            
            subscription = db.query(WechatSubscription).filter(
                WechatSubscription.user_id == user.id,
                WechatSubscription.is_subscribed == True,
                WechatSubscription.used_count < WechatSubscription.subscribe_count
            ).first()
            
            if not subscription:
                logger.debug(f"No valid subscription for user {user.id}")
                continue
            
            medication_name = plan.name
            take_time = scheduled_time.strftime("%Y-%m-%d %H:%M")
            dosage = f"{plan.dosage_amount}{plan.dosage_unit}"
            notes = plan.notes or "请按时服药"
            
            result = await wechat_service.send_medication_reminder(
                openid=user.wechat_openid,
                medication_name=medication_name,
                take_time=take_time,
                dosage=dosage,
                notes=notes
            )
            
            if result.get("errcode") == 0:
                subscription.used_count += 1
                subscription.last_used_at = datetime.now()
                db.commit()
                logger.info(f"Reminder sent for plan {plan.id}, user {user.id}")
            else:
                logger.warning(f"Failed to send reminder for plan {plan.id}: {result}")
    
    except Exception as e:
        logger.error(f"Error in send_medication_reminders: {e}")
    finally:
        db.close()

async def run_scheduler():
    logger.info("Starting medication reminder scheduler...")
    while True:
        try:
            await send_medication_reminders()
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
        
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(run_scheduler())
