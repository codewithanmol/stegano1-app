"""
Audio Steganography using LSB technique for WAV files
"""
import wave
import numpy as np
from crypto_utils import CryptoUtils
import io


class AudioSteganography:
    """Handle hiding and extracting data in audio files"""
    
    @staticmethod
    def get_capacity(audio_path: str) -> int:
        """Calculate maximum bytes that can be hidden in the audio file"""
        with wave.open(audio_path, 'rb') as audio:
            n_frames = audio.getnframes()
            n_channels = audio.getnchannels()
            total_samples = n_frames * n_channels
            # 1 bit per sample, minus space for length header
            return (total_samples // 8) - 4
    
    @staticmethod
    def encode(audio_path: str, secret_data: bytes, password: str = None) -> bytes:
        """Hide secret data in audio file using LSB technique"""
        # Encrypt if password provided
        if password:
            secret_data = CryptoUtils.encrypt(secret_data, password)
        
        # Load audio
        with wave.open(audio_path, 'rb') as audio:
            params = audio.getparams()
            n_frames = params.nframes
            n_channels = params.nchannels
            sampwidth = params.sampwidth
            frames = audio.readframes(n_frames)
        
        # Convert to numpy array
        if sampwidth == 2:
            dtype = np.int16
        else:
            dtype = np.uint8
        
        audio_array = np.frombuffer(frames, dtype=dtype)
        
        # Check capacity
        max_bytes = (len(audio_array) // 8) - 4
        if len(secret_data) > max_bytes:
            raise ValueError(f"Data too large. Max: {max_bytes} bytes, Got: {len(secret_data)} bytes")
        
        # Convert length to 4 bytes
        data_len = len(secret_data)
        len_bytes = data_len.to_bytes(4, byteorder='big')
        
        # Combine length and secret data
        full_data = len_bytes + secret_data
        
        # Convert data to binary
        binary_data = ''.join([format(byte, '08b') for byte in full_data])
        
        # Hide data in LSB
        audio_array = audio_array.copy()
        for i, bit in enumerate(binary_data):
            audio_array[i] = (audio_array[i] & ~1) | int(bit)
        
        # Save to bytes
        output = io.BytesIO()
        with wave.open(output, 'wb') as stego_audio:
            stego_audio.setparams(params)
            stego_audio.writeframes(audio_array.tobytes())
        
        return output.getvalue()
    
    @staticmethod
    def decode(audio_path: str, password: str = None) -> bytes:
        """Extract hidden data from audio file"""
        # Load audio
        with wave.open(audio_path, 'rb') as audio:
            params = audio.getparams()
            n_frames = params.nframes
            sampwidth = params.sampwidth
            frames = audio.readframes(n_frames)
        
        # Convert to numpy array
        if sampwidth == 2:
            dtype = np.int16
        else:
            dtype = np.uint8
        
        audio_array = np.frombuffer(frames, dtype=dtype)
        
        # Extract length (first 32 bits)
        len_bits = ''.join([str(audio_array[i] & 1) for i in range(32)])
        data_len = int(len_bits, 2)
        
        if data_len <= 0 or data_len > (len(audio_array) // 8):
            raise ValueError("No hidden data found or corrupted data")
        
        # Extract data
        total_bits = (data_len + 4) * 8
        data_bits = ''.join([str(audio_array[i] & 1) for i in range(32, total_bits)])
        
        # Convert binary to bytes
        secret_data = bytes([int(data_bits[i:i+8], 2) for i in range(0, len(data_bits), 8)])
        
        # Decrypt if password provided
        if password:
            secret_data = CryptoUtils.decrypt(secret_data, password)
        
        return secret_data
