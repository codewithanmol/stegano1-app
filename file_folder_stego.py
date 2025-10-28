"""
File and Folder Steganography - Hide files/folders inside images
"""
import zipfile
import io
from image_stego import ImageSteganography
from crypto_utils import CryptoUtils
import os
import base64


class FileFolderSteganography:
    """Handle hiding files and folders in images"""
    
    @staticmethod
    def encode_file(image_path: str, file_data: bytes, filename: str, password: str = None) -> bytes:
        """Hide a file inside an image"""
        # Create metadata: filename length (2 bytes) + filename + file data
        filename_bytes = filename.encode('utf-8')
        filename_len = len(filename_bytes).to_bytes(2, byteorder='big')
        
        combined_data = filename_len + filename_bytes + file_data
        
        # Use image steganography to hide the combined data
        return ImageSteganography.encode(image_path, combined_data, password)
    
    @staticmethod
    def decode_file(image_path: str, password: str = None) -> tuple:
        """Extract a file from an image, returns (filename, file_data)"""
        # Extract data using image steganography
        combined_data = ImageSteganography.decode(image_path, password)
        
        # Parse metadata
        filename_len = int.from_bytes(combined_data[:2], byteorder='big')
        filename = combined_data[2:2+filename_len].decode('utf-8')
        file_data = combined_data[2+filename_len:]
        
        return filename, file_data
    
    @staticmethod
    def encode_folder(image_path: str, folder_files: dict, password: str = None) -> bytes:
        """
        Hide multiple files/folder structure inside an image
        folder_files: dict where key=filepath, value=file_content_bytes
        """
        # Create a ZIP archive in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filepath, content in folder_files.items():
                zip_file.writestr(filepath, content)
        
        zip_data = zip_buffer.getvalue()
        
        # Hide ZIP in image
        return ImageSteganography.encode(image_path, zip_data, password)
    
    @staticmethod
    def decode_folder(image_path: str, password: str = None) -> dict:
        """
        Extract folder structure from image
        Returns dict where key=filepath, value=file_content_bytes
        """
        # Extract ZIP data from image
        zip_data = ImageSteganography.decode(image_path, password)
        
        # Extract files from ZIP
        folder_files = {}
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_file:
            for filename in zip_file.namelist():
                folder_files[filename] = zip_file.read(filename)
        
        return folder_files


class EmojiSteganography:
    """Hide data using emoji encoding"""
    
    # Use different emojis to represent different bit patterns
    EMOJI_MAP = {
        '00': '😀', '01': '😃', '10': '😄', '11': '😁',
        '000': '🎉', '001': '🎊', '010': '🎈', '011': '🎆',
        '100': '🎇', '101': '✨', '110': '🎀', '111': '🎁'
    }
    
    REVERSE_MAP_2BIT = {'😀': '00', '😃': '01', '😄': '10', '😁': '11'}
    REVERSE_MAP_3BIT = {'🎉': '000', '🎊': '001', '🎈': '010', '🎆': '011',
                         '🎇': '100', '✨': '101', '🎀': '110', '🎁': '111'}
    
    @staticmethod
    def encode(secret_data: bytes, password: str = None, bits_per_emoji: int = 2) -> str:
        """Convert secret data to emoji string"""
        # Encrypt if password provided
        if password:
            secret_data = CryptoUtils.encrypt(secret_data, password)
        
        # Encode length as base64 prefix
        length_marker = f"LEN:{len(secret_data)}:"
        
        # Convert to binary
        binary_data = ''.join([format(byte, '08b') for byte in secret_data])
        
        # Pad to make divisible by bits_per_emoji
        remainder = len(binary_data) % bits_per_emoji
        if remainder:
            binary_data += '0' * (bits_per_emoji - remainder)
        
        # Convert to emojis
        emoji_string = length_marker
        if bits_per_emoji == 2:
            emoji_map = EmojiSteganography.REVERSE_MAP_2BIT
            for i in range(0, len(binary_data), 2):
                bits = binary_data[i:i+2]
                for emoji, b in emoji_map.items():
                    if b == bits:
                        emoji_string += emoji
                        break
        else:  # 3 bits
            emoji_map = EmojiSteganography.REVERSE_MAP_3BIT
            for i in range(0, len(binary_data), 3):
                bits = binary_data[i:i+3]
                for emoji, b in emoji_map.items():
                    if b == bits:
                        emoji_string += emoji
                        break
        
        return emoji_string
    
    @staticmethod
    def decode(emoji_string: str, password: str = None, bits_per_emoji: int = 2) -> bytes:
        """Extract secret data from emoji string"""
        # Extract length
        if not emoji_string.startswith("LEN:"):
            raise ValueError("Invalid emoji steganography format")
        
        length_end = emoji_string.index(":", 4)
        data_len = int(emoji_string[4:length_end])
        emoji_data = emoji_string[length_end+1:]
        
        # Convert emojis to binary
        binary_data = ''
        if bits_per_emoji == 2:
            reverse_map = EmojiSteganography.REVERSE_MAP_2BIT
        else:
            reverse_map = EmojiSteganography.REVERSE_MAP_3BIT
        
        for emoji in emoji_data:
            if emoji in reverse_map:
                binary_data += reverse_map[emoji]
        
        # Convert binary to bytes
        secret_data = bytes([int(binary_data[i:i+8], 2) for i in range(0, data_len * 8, 8)])
        
        # Decrypt if password provided
        if password:
            secret_data = CryptoUtils.decrypt(secret_data, password)
        
        return secret_data
