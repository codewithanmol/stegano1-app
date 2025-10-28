"""
Text Steganography using zero-width characters and whitespace encoding
"""
from crypto_utils import CryptoUtils
import base64


class TextSteganography:
    """Handle hiding and extracting data in text using zero-width characters"""
    
    # Zero-width characters for binary encoding
    ZERO_WIDTH_SPACE = '\u200B'  # Binary 0
    ZERO_WIDTH_JOINER = '\u200D'  # Binary 1
    MARKER_START = '\u200C'  # Start marker
    MARKER_END = '\uFEFF'  # End marker
    
    @staticmethod
    def get_capacity(cover_text: str) -> int:
        """Estimate capacity in bytes (conservative estimate)"""
        # Can hide roughly 1 bit per character position
        return len(cover_text) // 8
    
    @staticmethod
    def encode(cover_text: str, secret_data: bytes, password: str = None) -> str:
        """Hide secret data in text using zero-width characters"""
        # Encrypt if password provided
        if password:
            secret_data = CryptoUtils.encrypt(secret_data, password)
        
        # Encode data as base64 for robustness
        encoded_data = base64.b64encode(secret_data)
        
        # Convert to binary
        binary_data = ''.join([format(byte, '08b') for byte in encoded_data])
        
        # Convert binary to zero-width characters
        hidden = TextSteganography.MARKER_START
        for bit in binary_data:
            if bit == '0':
                hidden += TextSteganography.ZERO_WIDTH_SPACE
            else:
                hidden += TextSteganography.ZERO_WIDTH_JOINER
        hidden += TextSteganography.MARKER_END
        
        # Insert hidden data in middle of cover text
        mid_point = len(cover_text) // 2
        result = cover_text[:mid_point] + hidden + cover_text[mid_point:]
        
        return result
    
    @staticmethod
    def decode(stego_text: str, password: str = None) -> bytes:
        """Extract hidden data from text"""
        # Find markers
        start_idx = stego_text.find(TextSteganography.MARKER_START)
        end_idx = stego_text.find(TextSteganography.MARKER_END)
        
        if start_idx == -1 or end_idx == -1:
            raise ValueError("No hidden data found in text")
        
        # Extract hidden characters
        hidden_section = stego_text[start_idx + 1:end_idx]
        
        # Convert zero-width characters back to binary
        binary_data = ''
        for char in hidden_section:
            if char == TextSteganography.ZERO_WIDTH_SPACE:
                binary_data += '0'
            elif char == TextSteganography.ZERO_WIDTH_JOINER:
                binary_data += '1'
        
        # Convert binary to bytes
        encoded_data = bytes([int(binary_data[i:i+8], 2) for i in range(0, len(binary_data), 8)])
        
        # Decode from base64
        try:
            secret_data = base64.b64decode(encoded_data)
        except Exception:
            raise ValueError("Failed to decode hidden data")
        
        # Decrypt if password provided
        if password:
            secret_data = CryptoUtils.decrypt(secret_data, password)
        
        return secret_data
    
    @staticmethod
    def encode_whitespace(cover_text: str, secret_message: str, password: str = None) -> str:
        """Alternative method: hide data using trailing whitespace"""
        secret_data = secret_message.encode('utf-8')
        
        # Encrypt if password provided
        if password:
            secret_data = CryptoUtils.encrypt(secret_data, password)
        
        # Convert to binary
        binary_data = ''.join([format(byte, '08b') for byte in secret_data])
        
        lines = cover_text.split('\n')
        if len(binary_data) > len(lines):
            raise ValueError(f"Cover text too short. Need {len(binary_data)} lines, have {len(lines)}")
        
        # Add trailing spaces (space=0, tab=1)
        result_lines = []
        for i, line in enumerate(lines):
            if i < len(binary_data):
                line = line.rstrip()  # Remove existing trailing whitespace
                if binary_data[i] == '0':
                    line += ' '
                else:
                    line += '\t'
            result_lines.append(line)
        
        return '\n'.join(result_lines)
