from sqlalchemy.orm import Session
from ..models import SystemLog
from ..logging_config import get_logger
from typing import Optional
import uuid

logger = get_logger(__name__)


def log_action(
    db: Session,
    *,
    user_id: Optional[uuid.UUID] = None,
    action: str,
    resource: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
):
    try:
        entry = SystemLog(
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address,
        )
        db.add(entry)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to write audit log: {e}")
