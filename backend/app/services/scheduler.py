"""
后台任务调度器
集成到FastAPI服务中，随服务启动自动运行
"""
import asyncio
from datetime import datetime
from typing import Optional
from ..database import SessionLocal
from ..models import MedicationPlan, MedicationLog, User, WechatSubscription
from ..services.wechat_service import wechat_service
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
                        
                        # 检查订阅状态
                        subscription = db.query(WechatSubscription).filter(
                            WechatSubscription.user_id == user.id,
                            WechatSubscription.is_subscribed == True,
                            WechatSubscription.used_count < WechatSubscription.subscribe_count
                        ).first()
                        
                        if not subscription:
                            logger.debug(f"用户订阅次数不足: user_id={user.id}")
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
    
    async def run(self):
        """运行定时任务"""
        logger.info("🕐 用药提醒定时任务已启动")
        self._running = True
        
        while self._running:
            try:
                await self.check_and_send_reminders()
            except Exception as e:
                logger.error(f"定时任务执行出错: {e}")
            
            await asyncio.sleep(self.check_interval)
        
        logger.info("🕐 用药提醒定时任务已停止")
    
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
            
        logger.info("✅ 用药提醒定时任务已停止")


# 全局调度器实例
scheduler = BackgroundScheduler()

# 需要导入timedelta
from datetime import timedelta
