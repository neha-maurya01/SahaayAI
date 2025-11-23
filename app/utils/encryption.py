from cryptography.fernet import Fernet
from app.config import settings
import base64
import hashlib

class EncryptionService:
    def __init__(self):
        # Ensure the key is 32 bytes for Fernet
        key = settings.ENCRYPTION_KEY.encode()
        if len(key) < 32:
            # Pad the key to 32 bytes
            key = key + b'0' * (32 - len(key))
        else:
            key = key[:32]
        
        # Fernet requires base64-encoded 32-byte key
        self.fernet = Fernet(base64.urlsafe_b64encode(key))
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not data:
            return ""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not encrypted_data:
            return ""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
    
    def hash_data(self, data: str) -> str:
        """Create a hash of data for indexing without exposing the actual value"""
        return hashlib.sha256(data.encode()).hexdigest()

encryption_service = EncryptionService()
