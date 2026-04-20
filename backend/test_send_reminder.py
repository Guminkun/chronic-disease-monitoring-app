"""
手动触发用药提醒测试脚本
用于在开发环境中测试订阅消息发送功能
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date
from app.database import SessionLocal
from app.models import MedicationPlan, MedicationLog, User, WechatSubscription
from app.services.wechat_service import wechat_service

async def test_send_reminder():
    """测试发送用药提醒"""
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("用药提醒测试脚本")
        print("=" * 60)
        
        # 1. 查询开启提醒的药品
        plans = db.query(MedicationPlan).filter(
            MedicationPlan.is_active == True,
            MedicationPlan.remind_enabled == True
        ).all()
        
        print(f"\n✅ 找到 {len(plans)} 个开启提醒的药品：")
        for i, plan in enumerate(plans, 1):
            print(f"  {i}. {plan.name}")
            print(f"     - 剂量: {plan.dosage_amount}{plan.dosage_unit}")
            print(f"     - 服药时间: {plan.taken_times}")
            print(f"     - remind_enabled: {plan.remind_enabled}")
        
        if not plans:
            print("\n⚠️  没有开启提醒的药品，请先添加药品并开启提醒")
            return
        
        # 2. 查询用户订阅状态
        print("\n" + "=" * 60)
        print("订阅状态检查：")
        
        for plan in plans:
            user = db.query(User).filter(User.id == plan.patient.user_id).first()
            if not user:
                print(f"❌ 药品 '{plan.name}' 没有关联用户")
                continue
            
            print(f"\n药品: {plan.name}")
            print(f"  用户ID: {user.id}")
            print(f"  wechat_openid: {user.wechat_openid or '未设置'}")
            
            if not user.wechat_openid:
                print(f"  ⚠️  用户没有wechat_openid，无法发送订阅消息")
                continue
            
            subscription = db.query(WechatSubscription).filter(
                WechatSubscription.user_id == user.id,
                WechatSubscription.is_subscribed == True
            ).first()
            
            if not subscription:
                print(f"  ⚠️  用户没有订阅记录")
                continue
            
            remaining = subscription.subscribe_count - subscription.used_count
            print(f"  订阅状态: ✅ 已订阅")
            print(f"  剩余次数: {remaining} 次")
            
            if remaining <= 0:
                print(f"  ⚠️  订阅次数已用完")
                continue
            
            # 3. 发送测试消息
            print(f"\n  正在发送测试消息...")
            
            medication_name = plan.name
            take_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            dosage = f"{plan.dosage_amount}{plan.dosage_unit}"
            notes = plan.notes or "测试消息：请按时服药"
            
            result = await wechat_service.send_medication_reminder(
                openid=user.wechat_openid,
                medication_name=medication_name,
                take_time=take_time,
                dosage=dosage,
                notes=notes
            )
            
            print(f"\n  发送结果：")
            print(f"  - errcode: {result.get('errcode')}")
            print(f"  - errmsg: {result.get('errmsg')}")
            
            if result.get("errcode") == 0:
                print(f"  ✅ 发送成功！")
                
                # 更新订阅次数
                subscription.used_count += 1
                subscription.last_used_at = datetime.now()
                db.commit()
                
                print(f"  剩余次数: {subscription.subscribe_count - subscription.used_count} 次")
                
                print("\n" + "=" * 60)
                print("⚠️  注意事项：")
                print("  1. 微信开发者工具中不会显示实际消息")
                print("  2. 请在手机微信中查看服务通知")
                print("  3. 如果在开发环境，可能无法实际送达")
                print("  4. 真实小程序环境中才能收到提醒")
                print("=" * 60)
            else:
                print(f"  ❌ 发送失败")
                print(f"  错误信息: {result}")
                
                # 常见错误码说明
                errcode = result.get('errcode')
                if errcode == 40003:
                    print(f"  原因: openid无效")
                elif errcode == 43101:
                    print(f"  原因: 用户拒绝接收消息")
                elif errcode == 47003:
                    print(f"  原因: 模板参数不准确")
                elif errcode == 41030:
                    print(f"  原因: page路径不正确")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("\n开始测试...")
    asyncio.run(test_send_reminder())
    print("\n测试完成！")
