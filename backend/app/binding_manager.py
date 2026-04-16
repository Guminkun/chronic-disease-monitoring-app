import random
import string
import time
from typing import Dict, Optional
import uuid

class BindingCodeManager:
    def __init__(self):
        # code -> {patient_id: uuid, expires_at: timestamp}
        self._codes: Dict[str, Dict] = {}
        # patient_id -> code (to prevent multiple codes per patient)
        self._patient_codes: Dict[uuid.UUID, str] = {}
        self.EXPIRATION_SECONDS = 300  # 5 minutes

    def generate_code(self, patient_id: uuid.UUID) -> str:
        # Cleanup expired codes lazily or just overwrite
        # If patient already has a code, return it if valid
        if patient_id in self._patient_codes:
            old_code = self._patient_codes[patient_id]
            if old_code in self._codes:
                if self._codes[old_code]["expires_at"] > time.time():
                    return old_code
                else:
                    # Expired, remove
                    del self._codes[old_code]
            
        # Generate new code (6 digits)
        code = "".join(random.choices(string.digits, k=6))
        while code in self._codes:
            code = "".join(random.choices(string.digits, k=6))
            
        self._codes[code] = {
            "patient_id": patient_id,
            "expires_at": time.time() + self.EXPIRATION_SECONDS
        }
        self._patient_codes[patient_id] = code
        return code

    def verify_code(self, code: str) -> Optional[uuid.UUID]:
        if code not in self._codes:
            return None
        
        data = self._codes[code]
        if data["expires_at"] < time.time():
            # Expired
            del self._codes[code]
            return None
            
        # Consume code (one-time use)
        patient_id = data["patient_id"]
        del self._codes[code]
        if patient_id in self._patient_codes:
            del self._patient_codes[patient_id]
            
        return patient_id

# Global instance
manager = BindingCodeManager()
