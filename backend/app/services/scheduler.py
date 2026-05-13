"""
后台任务调度器
集成到FastAPI服务中，随服务启动自动运行
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from ..database import SessionLocal
from ..models import MedicationPlan, MedicationLog, User, WechatSubscription, Reminder, Notification
from ..services.wechat_service import wechat_service
from ..config import settings
from ..logging_config import get_logger

logger = get_logger(__name__)


class BackgroundScheduler:
    """后台任务调度器"""
    
    def __init__(self):
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self.check_interval = 60  # 每60秒检查一次
    
    async def check_and_send_reminders(self):
        """检查并发送用药提醒"""
        db = SessionLocal()
        
        try:
            now = datetime.now()
            today = now.date()
            
            # 查询需要提醒的药品计划
            plans = db.query(MedicationPlan).filter(
                MedicationPlan.is_active == True,
                MedicationPlan.remind_enabled == True,
                MedicationPlan.start_date <= today,
            ).all()
            
            for plan in plans:
                # 检查是否暂停
                if plan.paused_until and plan.paused_until >= today:
                    continue
                
                # 检查是否已过期
                if plan.end_date and plan.end_date < today:
                    continue
                
                # 检查频率
                is_due = False
                if plan.frequency_type == "daily":
                    is_due = True
                elif plan.frequency_type == "interval":
                    try:
                        interval = int(plan.frequency_value or 1)
                        days_diff = (today - plan.start_date).days
                        if days_diff >= 0 and days_diff % (interval + 1) == 0:
                            is_due = True
                    except Exception as e:
                        logger.error(f"解析interval频率失败: {e}")
                elif plan.frequency_type == "specific_days":
                    try:
                        weekday = today.weekday() + 1
                        if str(weekday) in (plan.frequency_value or "").split(","):
                            is_due = True
                    except Exception as e:
                        logger.error(f"解析specific_days频率失败: {e}")
                
                if not is_due:
                    continue
                
                # 检查服药时间
                for take_time in (plan.taken_times or []):
                    try:
                        hour, minute = map(int, take_time.split(":"))
                        scheduled_time = datetime.combine(
                            today, 
                            datetime.min.time().replace(hour=hour, minute=minute)
                        )
                        
                        # 使用药品计划的提前提醒时间，默认5分钟
                        advance_minutes = plan.remind_advance_minutes or 5
                        
                        # 计算提醒时间窗口：提前N分钟到准点
                        reminder_window_start = scheduled_time - timedelta(minutes=advance_minutes)
                        reminder_window_end = scheduled_time
                        
                        # 检查当前时间是否在提醒窗口内
                        if not (reminder_window_start <= now <= reminder_window_end):
                            continue
                        
                        # 检查是否已发送过提醒
                        existing_log = db.query(MedicationLog).filter(
                            MedicationLog.plan_id == plan.id,
                            MedicationLog.scheduled_time == scheduled_time
                        ).first()
                        
                        if existing_log:
                            continue
                        
                        # 获取用户信息
                        user = db.query(User).filter(
                            User.id == plan.patient.user_id
                        ).first()
                        
                        if not user or not user.wechat_openid:
                            logger.debug(f"用户不存在或无openid: plan_id={plan.id}")
                            continue
                        
                        # 检查订阅状态 - 使用用药提醒模板ID
                        medication_template_id = settings.WECHAT_MEDICATION_TEMPLATE_ID
                        
                        subscription = db.query(WechatSubscription).filter(
                            WechatSubscription.user_id == user.id,
                            WechatSubscription.template_id == medication_template_id,
                            WechatSubscription.is_subscribed == True,
                            WechatSubscription.used_count < WechatSubscription.subscribe_count
                        ).first()
                        
                        if not subscription:
                            logger.info(f"用户未订阅用药提醒或订阅次数不足: user_id={user.id}, plan_id={plan.id}")
                            continue
                        
                        # 发送提醒
                        medication_name = plan.name
                        take_time_str = scheduled_time.strftime("%Y-%m-%d %H:%M")
                        dosage = f"{plan.dosage_amount}{plan.dosage_unit}"
                        notes = plan.notes or "请按时服药"
                        
                        result = await wechat_service.send_medication_reminder(
                            openid=user.wechat_openid,
                            medication_name=medication_name,
                            take_time=take_time_str,
                            dosage=dosage,
                            notes=notes
                        )
                        
                        if result.get("errcode") == 0:
                            # 创建用药日志记录，防止重复发送
                            new_log = MedicationLog(
                                plan_id=plan.id,
                                patient_id=plan.patient_id,
                                member_id=plan.member_id,
                                scheduled_time=scheduled_time,
                                status="pending"
                            )
                            db.add(new_log)
                            
                            # 更新订阅次数
                            subscription.used_count += 1
                            subscription.last_used_at = datetime.now()
                            db.commit()
                            
                            logger.info(
                                f"用药提醒发送成功: "
                                f"plan_id={plan.id}, "
                                f"user_id={user.id}, "
                                f"medication={medication_name}, "
                                f"time={take_time_str}"
                            )
                        else:
                            logger.warning(
                                f"用药提醒发送失败: "
                                f"plan_id={plan.id}, "
                                f"errcode={result.get('errcode')}, "
                                f"errmsg={result.get('errmsg')}"
                            )
                    
                    except Exception as e:
                        logger.error(f"处理服药时间失败: take_time={take_time}, error={e}")
                        continue
        
        except Exception as e:
            logger.error(f"检查用药提醒失败: {e}")
        finally:
            db.close()
    
    async def check_and_send_monitoring_reminders(self):
        """检查并发送监测提醒"""
        db = SessionLocal()
        
        try:
            now = datetime.now()
            today = now.date()
            
            # 查询需要发送的监测提醒
            reminders = db.query(Reminder).filter(
                Reminder.is_active == True,
                Reminder.type == 'recheck'
            ).all()
            
            for reminder in reminders:
                if not reminder.schedule_text:
                    continue
                
                # 解析提醒时间（格式：频率 时间，如"每天 08:00"）
                parts = reminder.schedule_text.split()
                if len(parts) < 2:
                    continue
                
                time_str = parts[-1]  # 最后一部分是时间
                freq = ' '.join(parts[:-1])  # 前面是频率
                
                try:
                    hour, minute = map(int, time_str.split(":"))
                    scheduled_time = datetime.combine(
                        today,
                        datetime.min.time().replace(hour=hour, minute=minute)
                    )
                    
                    # 检查频率是否匹配
                    if freq == '每天':
                        is_due = True
                    elif freq == '每两天':
                        days_diff = (today - reminder.created_at.date()).days
                        is_due = days_diff % 2 == 0
                    elif freq == '每三天':
                        days_diff = (today - reminder.created_at.date()).days
                        is_due = days_diff % 3 == 0
                    elif freq == '每周一次':
                        is_due = today.weekday() == 0  # 周一
                    elif freq == '每周两次':
                        days_diff = (today - reminder.created_at.date()).days
                        is_due = days_diff % 3 == 0 or days_diff % 3 == 1
                    else:
                        is_due = True
                    
                    if not is_due:
                        continue
                    
                    # 提醒窗口：提前5分钟到准点
                    reminder_window_start = scheduled_time - timedelta(minutes=5)
                    reminder_window_end = scheduled_time
                    
                    if not (reminder_window_start <= now <= reminder_window_end):
                        continue
                    
                    # 去重检查：今天是否已发送过该提醒
                    existing_notification = db.query(Notification).filter(
                        Notification.patient_id == reminder.patient_id,
                        Notification.title == reminder.title,
                        Notification.created_at >= datetime.combine(today, datetime.min.time())
                    ).first()
                    
                    if existing_notification:
                        continue
                    
                    # 获取用户信息
                    user = db.query(User).filter(
                        User.id == reminder.patient.user_id
                    ).first()
                    
                    if not user or not user.wechat_openid:
                        logger.debug(f"用户不存在或无openid: reminder_id={reminder.id}")
                        continue
                    
                    # 检查订阅状态 - 使用监测提醒模板ID
                    monitoring_template_id = settings.WECHAT_MONITORING_TEMPLATE_ID
                    
                    subscription = db.query(WechatSubscription).filter(
                        WechatSubscription.user_id == user.id,
                        WechatSubscription.template_id == monitoring_template_id,
                        WechatSubscription.is_subscribed == True,
                        WechatSubscription.used_count < WechatSubscription.subscribe_count
                    ).first()
                    
                    if not subscription:
                        logger.info(f"用户未订阅监测提醒或订阅次数不足: user_id={user.id}, reminder_id={reminder.id}")
                        continue
                    
                    # 发送监测提醒
                    task_name = reminder.title
                    task_time = scheduled_time.strftime("%Y-%m-%d %H:%M")
                    remark = "请按时测量并记录数据"
                    task_frequency = freq
                    
                    result = await wechat_service.send_monitoring_reminder(
                        openid=user.wechat_openid,
                        task_name=task_name,
                        task_time=task_time,
                        remark=remark,
                        task_frequency=task_frequency
                    )
                    
                    if result.get("errcode") == 0:
                        # 更新订阅次数
                        subscription.used_count += 1
                        subscription.last_used_at = datetime.now()
                        db.commit()
                        
                        logger.info(
                            f"监测提醒发送成功: "
                            f"reminder_id={reminder.id}, "
                            f"user_id={user.id}, "
                            f"title={task_name}, "
                            f"time={task_time}"
                        )
                    else:
                        logger.warning(
                            f"监测提醒发送失败: "
                            f"reminder_id={reminder.id}, "
                            f"errcode={result.get('errcode')}, "
                            f"errmsg={result.get('errmsg')}"
                        )
                
                except Exception as e:
                    logger.error(f"处理监测提醒失败: reminder_id={reminder.id}, error={e}")
                    continue
        
        except Exception as e:
            logger.error(f"检查监测提醒失败: {e}")
        finally:
            db.close()
    
    async def run(self):
        """运行定时任务"""
        logger.info("🕐 用药和监测提醒定时任务已启动")
        self._running = True
        
        while self._running:
            try:
                await self.check_and_send_reminders()
                await self.check_and_send_monitoring_reminders()
            except Exception as e:
                logger.error(f"定时任务执行出错: {e}")
            
            await asyncio.sleep(self.check_interval)
        
        logger.info("🕐 用药和监测提醒定时任务已停止")
    
    def start(self):
        """启动定时任务"""
        if self._running:
            logger.warning("定时任务已在运行中")
            return
        
        self._task = asyncio.create_task(self.run())
        logger.info("✅ 用药提醒定时任务已创建")
    
    async def stop(self):
        """停止定时任务"""
        if not self._running:
            return
        
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            
        logger.info("✅ 用药和监测提醒定时任务已停止")


# 全局调度器实例
scheduler = BackgroundScheduler()
