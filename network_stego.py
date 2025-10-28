"""
Network Steganography using packet header manipulation
"""
from scapy.all import IP, TCP, UDP, ICMP, Raw, wrpcap, rdpcap
from crypto_utils import CryptoUtils
import tempfile
import os


class NetworkSteganography:
    """Handle hiding and extracting data in network packets"""
    
    @staticmethod
    def encode_tcp_isn(secret_data: bytes, password: str = None, dest_ip: str = "192.168.1.1", 
                       dest_port: int = 80, num_packets: int = 10) -> bytes:
        """Hide data in TCP Initial Sequence Numbers"""
        # Encrypt if password provided
        if password:
            secret_data = CryptoUtils.encrypt(secret_data, password)
        
        # Prepend length header (4 bytes) to preserve exact data length
        data_len = len(secret_data)
        len_bytes = data_len.to_bytes(4, byteorder='big')
        full_data = len_bytes + secret_data
        
        # Convert data to integers (4 bytes per packet)
        packets = []
        chunk_size = 4
        
        for i in range(0, len(full_data), chunk_size):
            chunk = full_data[i:i+chunk_size]
            # Pad if necessary
            if len(chunk) < chunk_size:
                chunk = chunk + b'\x00' * (chunk_size - len(chunk))
            
            # Convert to integer for ISN
            isn = int.from_bytes(chunk, byteorder='big')
            
            # Create TCP SYN packet with custom ISN
            pkt = IP(dst=dest_ip)/TCP(dport=dest_port, flags='S', seq=isn)
            packets.append(pkt)
        
        # Save to pcap file
        temp_pcap = tempfile.NamedTemporaryFile(delete=False, suffix='.pcap')
        temp_pcap_path = temp_pcap.name
        temp_pcap.close()
        
        wrpcap(temp_pcap_path, packets)
        
        # Read and return bytes
        with open(temp_pcap_path, 'rb') as f:
            pcap_data = f.read()
        
        os.unlink(temp_pcap_path)
        return pcap_data
    
    @staticmethod
    def decode_tcp_isn(pcap_data: bytes, password: str = None) -> bytes:
        """Extract data from TCP Initial Sequence Numbers"""
        # Write to temp file
        temp_pcap = tempfile.NamedTemporaryFile(delete=False, suffix='.pcap')
        temp_pcap.write(pcap_data)
        temp_pcap_path = temp_pcap.name
        temp_pcap.close()
        
        # Read packets
        packets = rdpcap(temp_pcap_path)
        os.unlink(temp_pcap_path)
        
        # Extract ISNs
        full_data = b''
        for pkt in packets:
            if TCP in pkt and pkt[TCP].flags == 'S':
                isn = pkt[TCP].seq
                # Convert ISN to bytes (4 bytes)
                chunk = isn.to_bytes(4, byteorder='big')
                full_data += chunk
        
        if len(full_data) < 4:
            raise ValueError("No valid data found in packets")
        
        # Extract length from first 4 bytes
        data_len = int.from_bytes(full_data[:4], byteorder='big')
        
        # Extract exactly data_len bytes (no rstrip to preserve trailing nulls)
        if len(full_data) < 4 + data_len:
            raise ValueError(f"Incomplete data. Expected {data_len} bytes, got {len(full_data) - 4}")
        
        secret_data = full_data[4:4 + data_len]
        
        # Decrypt if password provided
        if password:
            secret_data = CryptoUtils.decrypt(secret_data, password)
        
        return secret_data
    
    @staticmethod
    def encode_ip_id(secret_data: bytes, password: str = None, dest_ip: str = "192.168.1.1") -> bytes:
        """Hide data in IP Identification field"""
        # Encrypt if password provided
        if password:
            secret_data = CryptoUtils.encrypt(secret_data, password)
        
        # Prepend length header (4 bytes) to preserve exact data length
        data_len = len(secret_data)
        len_bytes = data_len.to_bytes(4, byteorder='big')
        full_data = len_bytes + secret_data
        
        packets = []
        chunk_size = 2  # IP ID is 2 bytes
        
        for i in range(0, len(full_data), chunk_size):
            chunk = full_data[i:i+chunk_size]
            # Pad if necessary
            if len(chunk) < chunk_size:
                chunk = chunk + b'\x00' * (chunk_size - len(chunk))
            
            # Convert to integer for IP ID
            ip_id = int.from_bytes(chunk, byteorder='big')
            
            # Create ICMP packet with custom IP ID
            pkt = IP(dst=dest_ip, id=ip_id)/ICMP()
            packets.append(pkt)
        
        # Save to pcap file
        temp_pcap = tempfile.NamedTemporaryFile(delete=False, suffix='.pcap')
        temp_pcap_path = temp_pcap.name
        temp_pcap.close()
        
        wrpcap(temp_pcap_path, packets)
        
        # Read and return bytes
        with open(temp_pcap_path, 'rb') as f:
            pcap_data = f.read()
        
        os.unlink(temp_pcap_path)
        return pcap_data
    
    @staticmethod
    def decode_ip_id(pcap_data: bytes, password: str = None) -> bytes:
        """Extract data from IP Identification field"""
        # Write to temp file
        temp_pcap = tempfile.NamedTemporaryFile(delete=False, suffix='.pcap')
        temp_pcap.write(pcap_data)
        temp_pcap_path = temp_pcap.name
        temp_pcap.close()
        
        # Read packets
        packets = rdpcap(temp_pcap_path)
        os.unlink(temp_pcap_path)
        
        # Extract IP IDs
        full_data = b''
        for pkt in packets:
            if IP in pkt:
                ip_id = pkt[IP].id
                # Convert IP ID to bytes (2 bytes)
                chunk = ip_id.to_bytes(2, byteorder='big')
                full_data += chunk
        
        if len(full_data) < 4:
            raise ValueError("No valid data found in packets")
        
        # Extract length from first 4 bytes
        data_len = int.from_bytes(full_data[:4], byteorder='big')
        
        # Extract exactly data_len bytes (no rstrip to preserve trailing nulls)
        if len(full_data) < 4 + data_len:
            raise ValueError(f"Incomplete data. Expected {data_len} bytes, got {len(full_data) - 4}")
        
        secret_data = full_data[4:4 + data_len]
        
        # Decrypt if password provided
        if password:
            secret_data = CryptoUtils.decrypt(secret_data, password)
        
        return secret_data
