"""
Video Steganography using frame-based LSB technique
"""
"""import cv2
import numpy as np
from crypto_utils import CryptoUtils
import tempfile
import os


class VideoSteganography:
    """Handle hiding and extracting data in video files"""
    
    @staticmethod
    def get_capacity(video_path: str) -> int:
        """Calculate maximum bytes that can be hidden in the video"""
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return 0
        
        pixels_per_frame = frame.size
        total_pixels = pixels_per_frame * total_frames
        # 1 bit per pixel, minus space for header
        return (total_pixels // 8) - 4
    
    @staticmethod
    def encode(video_path: str, secret_data: bytes, password: str = None) -> bytes:
        """Hide secret data in video using LSB technique"""
        # Encrypt if password provided
        if password:
            secret_data = CryptoUtils.encrypt(secret_data, password)
        
        # Check capacity before processing
        max_bytes = VideoSteganography.get_capacity(video_path)
        if len(secret_data) > max_bytes:
            raise ValueError(f"Data too large. Max: {max_bytes} bytes, Got: {len(secret_data)} bytes")
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        # Create temporary output file
        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_output_path = temp_output.name
        temp_output.close()
        
        out = cv2.VideoWriter(temp_output_path, fourcc, fps, (width, height))
        
        # Convert length to 4 bytes
        data_len = len(secret_data)
        len_bytes = data_len.to_bytes(4, byteorder='big')
        
        # Combine length and secret data
        full_data = len_bytes + secret_data
        
        # Convert data to binary
        binary_data = ''.join([format(byte, '08b') for byte in full_data])
        total_bits_needed = len(binary_data)
        
        bit_index = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                # Video ended but we haven't embedded all bits
                if bit_index < total_bits_needed:
                    cap.release()
                    out.release()
                    os.unlink(temp_output_path)
                    raise ValueError(f"Video too short. Embedded {bit_index}/{total_bits_needed} bits")
                break
            
            # Make a copy to avoid modifying original
            frame = frame.copy()
            flat_frame = frame.flatten()
            
            # Hide data in this frame
            for i in range(len(flat_frame)):
                if bit_index >= total_bits_needed:
                    break
                flat_frame[i] = (flat_frame[i] & 0xFE) | int(binary_data[bit_index])
                bit_index += 1
            
            # Reshape and write frame
            stego_frame = flat_frame.reshape(frame.shape)
            out.write(stego_frame)
            
            # If all bits embedded, write remaining frames unchanged
            if bit_index >= total_bits_needed:
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    out.write(frame)
                break
        
        cap.release()
        out.release()
        
        # Read the output file
        with open(temp_output_path, 'rb') as f:
            video_bytes = f.read()
        
        # Clean up
        os.unlink(temp_output_path)
        
        return video_bytes
    
    @staticmethod
    def decode(video_path: str, password: str = None) -> bytes:
        """Extract hidden data from video"""
        cap = cv2.VideoCapture(video_path)
        
        # Extract all bits in a single pass (no rewinding)
        extracted_bits = []
        total_bits_needed = None  # Will be set once header is read
        
        # Read frames and extract LSBs
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            flat_frame = frame.flatten()
            
            # If we haven't read the header yet (first 32 bits)
            if total_bits_needed is None:
                # Extract bits to complete header
                for i in range(len(flat_frame)):
                    extracted_bits.append(str(flat_frame[i] & 1))
                    if len(extracted_bits) >= 32:
                        # Parse the length from first 32 bits
                        len_bits = ''.join(extracted_bits[:32])
                        data_len = int(len_bits, 2)
                        
                        if data_len <= 0 or data_len > 100000000:  # Sanity check
                            cap.release()
                            raise ValueError(f"Invalid data length: {data_len}")
                        
                        total_bits_needed = (data_len + 4) * 8
                        
                        # Continue extracting remaining bits in this frame
                        for j in range(i + 1, len(flat_frame)):
                            if len(extracted_bits) >= total_bits_needed:
                                break
                            extracted_bits.append(str(flat_frame[j] & 1))
                        break
                
                # Check if we have all bits after reading this frame
                if total_bits_needed is not None and len(extracted_bits) >= total_bits_needed:
                    break
            else:
                # Header already read, extract remaining data
                for i in range(len(flat_frame)):
                    if len(extracted_bits) >= total_bits_needed:
                        break
                    extracted_bits.append(str(flat_frame[i] & 1))
                
                if len(extracted_bits) >= total_bits_needed:
                    break
        
        cap.release()
        
        # Validate we have enough bits
        if len(extracted_bits) < 32:
            raise ValueError("Video too short to contain header")
        
        # Re-parse length to ensure consistency
        len_bits = ''.join(extracted_bits[:32])
        data_len = int(len_bits, 2)
        total_bits_needed = (data_len + 4) * 8
        
        if len(extracted_bits) < total_bits_needed:
            raise ValueError(f"Video too short or corrupted. Expected {total_bits_needed} bits, got {len(extracted_bits)}")
        
        # Convert to bytes (skip first 32 bits which are length, extract exactly data_len bytes)
        data_bits = ''.join(extracted_bits[32:total_bits_needed])
        secret_data = bytes([int(data_bits[i:i+8], 2) for i in range(0, len(data_bits), 8)])
        
        # Decrypt if password provided
        if password:
            secret_data = CryptoUtils.decrypt(secret_data, password)
        
        return secret_data
"""
