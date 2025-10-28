"""
Image Steganography using LSB (Least Significant Bit) technique
"""
from PIL import Image
import numpy as np
from crypto_utils import CryptoUtils
import io


class ImageSteganography:
    """Handle hiding and extracting data in images using LSB"""
    
    @staticmethod
    def get_capacity(image_path: str) -> int:
        """Calculate maximum bytes that can be hidden in the image"""
        img = Image.open(image_path)
        img_array = np.array(img)
        total_pixels = img_array.size
        # 1 bit per color channel, minus space for length header
        return (total_pixels // 8) - 4
    
    @staticmethod
    def encode(image_path: str, secret_data: bytes, password: str = None) -> bytes:
        """Hide secret data in image using LSB technique"""
        # Encrypt if password provided
        if password:
            secret_data = CryptoUtils.encrypt(secret_data, password)
        
        # Load image
        img = Image.open(image_path)
        img_array = np.array(img, dtype=np.uint8)
        
        # Check capacity
        max_bytes = (img_array.size // 8) - 4
        if len(secret_data) > max_bytes:
            raise ValueError(f"Data too large. Max: {max_bytes} bytes, Got: {len(secret_data)} bytes")
        
        # Flatten image array
        flat_img = img_array.flatten()
        
        # Convert length to 4 bytes (32-bit integer)
        data_len = len(secret_data)
        len_bytes = data_len.to_bytes(4, byteorder='big')
        
        # Combine length and secret data
        full_data = len_bytes + secret_data
        
        # Convert data to binary
        binary_data = ''.join([format(byte, '08b') for byte in full_data])
        
        # Hide data in LSB
        for i, bit in enumerate(binary_data):
            flat_img[i] = (flat_img[i] & 0xFE) | int(bit)
        
        # Reshape and save
        stego_img = flat_img.reshape(img_array.shape)
        result_img = Image.fromarray(stego_img)
        
        # Save to bytes
        img_bytes = io.BytesIO()
        result_img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    
    @staticmethod
    def decode(image_path: str, password: str = None) -> bytes:
        """Extract hidden data from image"""
        # Load image
        img = Image.open(image_path)
        img_array = np.array(img, dtype=np.uint8)
        flat_img = img_array.flatten()
        
        # Extract length (first 32 bits)
        len_bits = ''.join([str(flat_img[i] & 1) for i in range(32)])
        data_len = int(len_bits, 2)
        
        if data_len <= 0 or data_len > (flat_img.size // 8):
            raise ValueError("No hidden data found or corrupted data")
        
        # Extract data
        total_bits = (data_len + 4) * 8
        data_bits = ''.join([str(flat_img[i] & 1) for i in range(32, total_bits)])
        
        # Convert binary to bytes
        secret_data = bytes([int(data_bits[i:i+8], 2) for i in range(0, len(data_bits), 8)])
        
        # Decrypt if password provided
        if password:
            secret_data = CryptoUtils.decrypt(secret_data, password)
        
        return secret_data
