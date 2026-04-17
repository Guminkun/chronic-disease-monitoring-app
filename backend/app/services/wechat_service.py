import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from ..config import settings
from ..logging_config import get_logger

logger = get_logger(__name__)

class WechatSubscriptionService:
    def __init__(self):
        self.appid = settings.WECHAT_APPID
        self.secret = settings.WECHAT_SECRET
        self.template_id = getattr(settings, 'WECHAT_MEDICATION_TEMPLATE_ID', '')
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
    
    async def get_access_token(self) -> Optional[str]:
        if self._access_token and self._token_expires_at and datetime.now() < self._token_expires_at:
            return self._access_token
        
        if not self.appid or not self.secret:
            logger.warning("WeChat appid or secret not configured")
            return None
        
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.secret
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                data = response.json()
                
                if "access_token" in data:
                    self._access_token = data["access_token"]
                    expires_in = data.get("expires_in", 7200)
                    self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
                    logger.info(f"WeChat access token obtained, expires in {expires_in}s")
                    return self._access_token
                else:
                    logger.error(f"Failed to get WeChat access token: {data}")
                    return None
        except Exception as e:
            logger.error(f"Error getting WeChat access token: {e}")
            return None
    
    async def get_openid_by_code(self, code: str) -> Optional[str]:
        """通过微信登录code获取openid"""
        if not self.appid or not self.secret:
            logger.warning("WeChat appid or secret not configured, returning mock openid for dev")
            return f"mock_openid_{code[:8]}"
        
        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            "appid": self.appid,
            "secret": self.secret,
            "js_code": code,
            "grant_type": "authorization_code"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                data = response.json()
                
                if "openid" in data:
                    logger.info(f"Got openid from code")
                    return data["openid"]
                else:
                    logger.error(f"Failed to get openid from code: {data}")
                    return None
        except Exception as e:
            logger.error(f"Error getting openid from code: {e}")
            return None
    
    async def send_medication_reminder(
        self,
        openid: str,
        medication_name: str,
        take_time: str,
        dosage: str,
        notes: str = ""
    ) -> Dict[str, Any]:
        if not self.template_id:
            logger.error("WeChat medication template ID not configured")
            return {"errcode": -1, "errmsg": "Template ID not configured"}
        
        access_token = await self.get_access_token()
        if not access_token:
            return {"errcode": -1, "errmsg": "Failed to get access token"}
        
        url = f"https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}"
        
        if notes and len(notes) > 20:
            notes = notes[:17] + "..."
        
        payload = {
            "touser": openid,
            "template_id": self.template_id,
            "page": "pages/medication/index",
            "data": {
                "thing1": {"value": medication_name[:20] if len(medication_name) > 20 else medication_name},
                "time2": {"value": take_time},
                "thing3": {"value": dosage[:20] if len(dosage) > 20 else dosage},
                "thing4": {"value": notes[:20] if notes else "请按时服药"}
            },
            "miniprogram_state": "formal"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                result = response.json()
                
                if result.get("errcode") == 0:
                    logger.info(f"Medication reminder sent successfully to {openid}")
                else:
                    logger.warning(f"Failed to send medication reminder: {result}")
                
                return result
        except Exception as e:
            logger.error(f"Error sending medication reminder: {e}")
            return {"errcode": -1, "errmsg": str(e)}
    
    async def send_subscription_message(
        self,
        openid: str,
        template_id: str,
        data: Dict[str, Any],
        page: str = ""
    ) -> Dict[str, Any]:
        access_token = await self.get_access_token()
        if not access_token:
            return {"errcode": -1, "errmsg": "Failed to get access token"}
        
        url = f"https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={access_token}"
        
        payload = {
            "touser": openid,
            "template_id": template_id,
            "page": page,
            "data": data,
            "miniprogram_state": "formal"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                result = response.json()
                return result
        except Exception as e:
            logger.error(f"Error sending subscription message: {e}")
            return {"errcode": -1, "errmsg": str(e)}


wechat_service = WechatSubscriptionService()
