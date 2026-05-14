from cryptography.fernet import Fernet
from ..config import settings
from ..logging_config import get_logger
import hashlib
import base64

logger = get_logger(__name__)

_fernet: Fernet | None = None


def _get_fernet() -> Fernet | None:
    global _fernet
    if _fernet is not None:
        return _fernet
    try:
        key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key)
        _fernet = Fernet(fernet_key)
        return _fernet
    except Exception as e:
        logger.error(f"Failed to initialize encryption: {e}")
        return None


def encrypt_field(plaintext: str | None) -> str | None:
    if not plaintext:
        return plaintext
    f = _get_fernet()
    if not f:
        return plaintext
    try:
        return f.encrypt(plaintext.encode()).decode()
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        return plaintext


def decrypt_field(ciphertext: str | None) -> str | None:
    if not ciphertext:
        return ciphertext
    f = _get_fernet()
    if not f:
        return ciphertext
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        return ciphertext
