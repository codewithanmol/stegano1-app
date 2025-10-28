# Overview

This is a comprehensive steganography tool built with Python and Streamlit that enables users to hide and extract secret data across multiple media types including images, audio files, video files, text, network packets, and even emojis. The application uses LSB (Least Significant Bit) techniques for media files, zero-width characters for text, and packet header manipulation for network data. It includes optional password-based AES-256-GCM encryption for enhanced security.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture

**Framework**: Streamlit web application
- Single-page application with sidebar navigation
- Two primary modes: Encode (Hide) and Decode (Extract)
- Eight steganography types supported: Image, Audio, Video, Text, File in Image, Folder in Image, Network Packets, and Emoji
- Wide layout configuration for better UX with media files
- Temporary file handling for uploaded content

**Rationale**: Streamlit was chosen for rapid prototyping and provides built-in file upload/download widgets ideal for media processing applications. The framework handles session state and UI rendering automatically.

## Backend Architecture

**Modular Design**: Separate steganography modules for each media type
- `image_stego.py` - Image steganography using LSB on pixel data
- `audio_stego.py` - Audio steganography using LSB on WAV file samples
- `video_stego.py` - Video steganography using LSB across video frames
- `text_stego.py` - Text steganography using zero-width Unicode characters
- `network_stego.py` - Network packet steganography using TCP sequence numbers
- `file_folder_stego.py` - File/folder embedding in images with ZIP compression
- `crypto_utils.py` - Centralized encryption/decryption utilities

**Design Pattern**: Each steganography class follows a consistent interface with static methods for `encode()`, `decode()`, and `get_capacity()` operations. This provides a uniform API across different steganography techniques.

**Rationale**: Modular architecture enables independent development and testing of each steganography technique. Static methods were chosen since no state needs to be maintained between operations, simplifying the interface.

## Data Processing Pipeline

**LSB Steganography Flow**:
1. Optional encryption using AES-256-GCM with password-derived keys
2. Data length header prepended (4 bytes, big-endian)
3. Binary conversion of payload
4. LSB manipulation in media file (images, audio, video)
5. Output generation in original media format

**Text Steganography Flow**:
1. Optional encryption
2. Base64 encoding for robustness
3. Binary to zero-width character mapping
4. Insertion at midpoint of cover text with start/end markers

**Network Steganography Flow**:
1. Optional encryption
2. Data chunking into 4-byte segments
3. Encoding into TCP Initial Sequence Numbers
4. PCAP file generation using Scapy

**Rationale**: LSB technique provides good capacity-to-imperceptibility ratio. Length headers enable exact data extraction. Base64 encoding in text steganography ensures robustness against text processing. Zero-width characters are invisible to users while preserving text meaning.

## Encryption Layer

**Implementation**: AES-256-GCM mode with PBKDF2 key derivation
- 16-byte random salt generation
- 100,000 PBKDF2 iterations for key strengthening
- GCM mode provides authenticated encryption
- Encrypted payload structure: salt(16) + nonce(16) + tag(16) + ciphertext

**Rationale**: AES-256-GCM chosen for authenticated encryption preventing tampering. PBKDF2 with high iteration count protects against brute-force attacks. Salt prevents rainbow table attacks.

## Media Processing Libraries

**Image Processing**: PIL (Pillow) with NumPy arrays
- Converts images to NumPy arrays for pixel manipulation
- Preserves image format and metadata
- In-memory processing with BytesIO for Streamlit compatibility

**Audio Processing**: Python wave module with NumPy
- WAV format support for lossless audio
- 16-bit and 8-bit sample width handling
- Frame-level manipulation for LSB encoding

**Video Processing**: OpenCV (cv2)
- Frame-by-frame video processing
- MP4V codec for output generation
- Temporary file handling for video encoding

**Network Processing**: Scapy
- Packet crafting with custom TCP sequence numbers
- PCAP file generation and parsing
- IP/TCP/UDP protocol support

**Rationale**: These libraries are industry-standard, well-maintained, and provide the low-level access needed for steganography operations. NumPy enables efficient array operations for large media files.

## File Handling

**Approach**: Temporary file system with cleanup
- `tempfile.NamedTemporaryFile` for uploaded content
- File extension preservation for format detection
- In-memory processing where possible (images, text)
- Disk-based processing for large media (audio, video)

**ZIP Archive Support**: Folder steganography uses in-memory ZIP creation
- Multiple files compressed into single archive
- Preserves folder structure and filenames
- Reduces payload size for better capacity utilization

**Rationale**: Temporary files avoid persistence concerns in web applications. In-memory processing reduces I/O overhead. ZIP compression maximizes hiding capacity for multi-file scenarios.

# External Dependencies

## Core Libraries

**Streamlit** (`streamlit`)
- Purpose: Web application framework
- Used for: UI rendering, file uploads, user interaction

**Pillow** (`PIL`)
- Purpose: Image processing
- Used for: Image loading, manipulation, and saving

**NumPy** (`numpy`)
- Purpose: Numerical computing
- Used for: Array operations on pixel/sample data

**OpenCV** (`cv2`)
- Purpose: Video processing
- Used for: Video frame extraction and encoding

**PyCryptodome** (`Crypto`)
- Purpose: Cryptographic operations
- Used for: AES encryption, key derivation (PBKDF2)

**Scapy** (`scapy`)
- Purpose: Network packet manipulation
- Used for: Creating and parsing PCAP files

**Standard Library Modules**:
- `wave`: Audio file processing
- `zipfile`: Archive creation for folders
- `io`: In-memory file handling
- `base64`: Text encoding
- `tempfile`: Temporary file management
- `os`: File system operations

## Potential Future Dependencies

The architecture supports extension to additional media types or storage backends, which might require:
- Database integration for storing stego-objects metadata
- Cloud storage APIs for large file handling
- Additional media codecs for format support