"""Encryption utilities for sensitive data"""
import os
import logging
from cryptography.fernet import Fernet
from typing import Optional

logger = logging.getLogger(__name__)

# Cache the cipher instance
_cipher: Optional[Fernet] = None


def get_cipher() -> Fernet:
    """Get or create the encryption cipher"""
    global _cipher
    
    if _cipher is None:
        # Try to get key from environment
        key = os.environ.get("MS_TOKEN_ENCRYPTION_KEY")
        
        if not key:
            # Generate a new key (only for development)
            key = Fernet.generate_key().decode()
            logger.warning(
                "MS_TOKEN_ENCRYPTION_KEY not set. Generated temporary key. "
                "Set MS_TOKEN_ENCRYPTION_KEY environment variable for production."
            )
            # Store it for this session
            os.environ["MS_TOKEN_ENCRYPTION_KEY"] = key
        else:
            # Ensure key is bytes
            key = key.encode() if isinstance(key, str) else key
        
        _cipher = Fernet(key)
    
    return _cipher


def encrypt_token(token: str) -> str:
    """Encrypt a token string"""
    if not token:
        return ""
    
    try:
        cipher = get_cipher()
        encrypted = cipher.encrypt(token.encode())
        return encrypted.decode()
    except Exception as e:
        logger.error(f"Failed to encrypt token: {e}")
        raise ValueError("Token encryption failed")


def decrypt_token(encrypted: str) -> str:
    """Decrypt an encrypted token string"""
    if not encrypted:
        return ""
    
    try:
        cipher = get_cipher()
        decrypted = cipher.decrypt(encrypted.encode())
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Failed to decrypt token: {e}")
        raise ValueError("Token decryption failed")


def generate_encryption_key() -> str:
    """Generate a new encryption key for setup"""
    return Fernet.generate_key().decode()