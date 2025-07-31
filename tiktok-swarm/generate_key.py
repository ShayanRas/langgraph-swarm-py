#!/usr/bin/env python3
"""Generate a valid Fernet encryption key"""
from cryptography.fernet import Fernet

key = Fernet.generate_key()
print(f"Generated encryption key: {key.decode()}")
print("\nAdd this to your .env file:")
print(f"MS_TOKEN_ENCRYPTION_KEY={key.decode()}")