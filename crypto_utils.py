"""
Encryption and decryption utilities for steganography
"""
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import hashlib
import base64


class CryptoUtils:
    """Handle encryption and decryption with password protection"""
    
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """Derive a key from password using PBKDF2"""
        return PBKDF2(password.encode(), salt, dkLen=32, count=100000)
    
    @staticmethod
    def encrypt(data: bytes, password: str) -> bytes:
        """Encrypt data with password using AES-256-GCM"""
        salt = get_random_bytes(16)
        key = CryptoUtils.derive_key(password, salt)
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        
        # Return: salt(16) + nonce(16) + tag(16) + ciphertext
        return salt + cipher.nonce + tag + ciphertext
    
    @staticmethod
    def decrypt(encrypted_data: bytes, password: str) -> bytes:
        """Decrypt data with password"""
        try:
            salt = encrypted_data[:16]
            nonce = encrypted_data[16:32]
            tag = encrypted_data[32:48]
            ciphertext = encrypted_data[48:]
            
            key = CryptoUtils.derive_key(password, salt)
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            return plaintext
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}. Wrong password?")
