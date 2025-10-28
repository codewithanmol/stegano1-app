"""
Comprehensive Steganography Tool
Hide and extract data from images, audio, video, text, files, folders, network packets, and emojis
"""
import streamlit as st
import io
import base64
from PIL import Image
import tempfile
import os

# Import steganography modules
from image_stego import ImageSteganography
from audio_stego import AudioSteganography
from text_stego import TextSteganography
#from video_stego import VideoSteganography
from network_stego import NetworkSteganography
from file_folder_stego import FileFolderSteganography, EmojiSteganography


st.set_page_config(
    page_title="Steganography Tool",
    page_icon="🔒",
    layout="wide"
)

st.title("🔒 Advanced Steganography Tool")
st.markdown("Hide and extract secret data in images, audio, video, text, files, folders, network packets, and emojis")

# Sidebar for navigation
st.sidebar.title("Navigation")
mode = st.sidebar.radio("Choose Mode:", ["Encode (Hide)", "Decode (Extract)"])
stego_type = st.sidebar.selectbox(
    "Steganography Type:",
    ["Image", "Audio", "Video", "Text", "File in Image", "Folder in Image", "Network Packets", "Emoji"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip**: Use password protection for enhanced security!")


def save_uploaded_file(uploaded_file):
    """Save uploaded file to temp location and return path"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1])
    temp_file.write(uploaded_file.read())
    temp_file.close()
    return temp_file.name


# ========== IMAGE STEGANOGRAPHY ==========
if stego_type == "Image":
    st.header("🖼️ Image Steganography")
    st.markdown("Hide secret messages or data inside images using LSB technique")
    
    if mode == "Encode (Hide)":
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Cover Image")
            cover_image = st.file_uploader("Upload cover image (PNG/BMP recommended)", 
                                          type=['png', 'bmp', 'jpg', 'jpeg'], key="img_cover")
            
            if cover_image:
                img = Image.open(cover_image)
                st.image(img, caption="Cover Image", use_container_width=True)
                
                # Save temp file for capacity check
                temp_path = save_uploaded_file(cover_image)
                capacity = ImageSteganography.get_capacity(temp_path)
                st.success(f"✅ Capacity: {capacity:,} bytes ({capacity/1024:.2f} KB)")
                os.unlink(temp_path)
        
        with col2:
            st.subheader("Secret Data")
            secret_text = st.text_area("Enter secret message:", height=150)
            password = st.text_input("Password (optional):", type="password", key="img_enc_pass")
            
            if st.button("🔒 Hide Data in Image", type="primary"):
                if cover_image and secret_text:
                    try:
                        temp_path = save_uploaded_file(cover_image)
                        secret_data = secret_text.encode('utf-8')
                        
                        pwd = password if password else None
                        stego_image_bytes = ImageSteganography.encode(temp_path, secret_data, pwd)
                        os.unlink(temp_path)
                        
                        st.success("✅ Data hidden successfully!")
                        
                        # Display stego image
                        stego_img = Image.open(io.BytesIO(stego_image_bytes))
                        st.image(stego_img, caption="Stego Image (with hidden data)", use_container_width=True)
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Stego Image",
                            data=stego_image_bytes,
                            file_name="stego_image.png",
                            mime="image/png"
                        )
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please provide both cover image and secret message")
    
    else:  # Decode
        st.subheader("Extract Hidden Data")
        stego_image = st.file_uploader("Upload stego image:", type=['png', 'bmp', 'jpg', 'jpeg'], key="img_stego")
        password = st.text_input("Password (if used):", type="password", key="img_dec_pass")
        
        if st.button("🔓 Extract Hidden Data", type="primary"):
            if stego_image:
                try:
                    temp_path = save_uploaded_file(stego_image)
                    pwd = password if password else None
                    secret_data = ImageSteganography.decode(temp_path, pwd)
                    os.unlink(temp_path)
                    
                    st.success("✅ Data extracted successfully!")
                    secret_text = secret_data.decode('utf-8')
                    st.text_area("Extracted Secret Message:", value=secret_text, height=200)
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please upload a stego image")


# ========== AUDIO STEGANOGRAPHY ==========
elif stego_type == "Audio":
    st.header("🎵 Audio Steganography")
    st.markdown("Hide secret data inside audio files (WAV format)")
    
    if mode == "Encode (Hide)":
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Cover Audio")
            cover_audio = st.file_uploader("Upload cover audio (WAV only)", type=['wav'], key="aud_cover")
            
            if cover_audio:
                st.audio(cover_audio, format='audio/wav')
                
                temp_path = save_uploaded_file(cover_audio)
                capacity = AudioSteganography.get_capacity(temp_path)
                st.success(f"✅ Capacity: {capacity:,} bytes ({capacity/1024:.2f} KB)")
                os.unlink(temp_path)
        
        with col2:
            st.subheader("Secret Data")
            secret_text = st.text_area("Enter secret message:", height=150, key="aud_secret")
            password = st.text_input("Password (optional):", type="password", key="aud_enc_pass")
            
            if st.button("🔒 Hide Data in Audio", type="primary"):
                if cover_audio and secret_text:
                    try:
                        temp_path = save_uploaded_file(cover_audio)
                        secret_data = secret_text.encode('utf-8')
                        
                        pwd = password if password else None
                        stego_audio_bytes = AudioSteganography.encode(temp_path, secret_data, pwd)
                        os.unlink(temp_path)
                        
                        st.success("✅ Data hidden successfully!")
                        st.audio(stego_audio_bytes, format='audio/wav')
                        
                        st.download_button(
                            label="📥 Download Stego Audio",
                            data=stego_audio_bytes,
                            file_name="stego_audio.wav",
                            mime="audio/wav"
                        )
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please provide both cover audio and secret message")
    
    else:  # Decode
        st.subheader("Extract Hidden Data")
        stego_audio = st.file_uploader("Upload stego audio:", type=['wav'], key="aud_stego")
        password = st.text_input("Password (if used):", type="password", key="aud_dec_pass")
        
        if st.button("🔓 Extract Hidden Data", type="primary"):
            if stego_audio:
                try:
                    temp_path = save_uploaded_file(stego_audio)
                    pwd = password if password else None
                    secret_data = AudioSteganography.decode(temp_path, pwd)
                    os.unlink(temp_path)
                    
                    st.success("✅ Data extracted successfully!")
                    secret_text = secret_data.decode('utf-8')
                    st.text_area("Extracted Secret Message:", value=secret_text, height=200)
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please upload a stego audio file")


# ========== VIDEO STEGANOGRAPHY ==========
"""#elif stego_type == "Video":
 ##  st.markdown("Hide secret data inside video files")
    
    if mode == "Encode (Hide)":
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Cover Video")
            cover_video = st.file_uploader("Upload cover video (MP4, AVI)", type=['mp4', 'avi'], key="vid_cover")
            
            if cover_video:
                st.video(cover_video)
                
                temp_path = save_uploaded_file(cover_video)
                capacity = VideoSteganography.get_capacity(temp_path)
                st.success(f"✅ Capacity: {capacity:,} bytes ({capacity/1024:.2f} KB)")
                os.unlink(temp_path)
        
        with col2:
            st.subheader("Secret Data")
            secret_text = st.text_area("Enter secret message:", height=150, key="vid_secret")
            password = st.text_input("Password (optional):", type="password", key="vid_enc_pass")
            
            if st.button("🔒 Hide Data in Video", type="primary"):
                if cover_video and secret_text:
                    try:
                        with st.spinner("Processing video... This may take a moment..."):
                            temp_path = save_uploaded_file(cover_video)
                            secret_data = secret_text.encode('utf-8')
                            
                            pwd = password if password else None
                            stego_video_bytes = VideoSteganography.encode(temp_path, secret_data, pwd)
                            os.unlink(temp_path)
                        
                        st.success("✅ Data hidden successfully!")
                        st.video(stego_video_bytes)
                        
                        st.download_button(
                            label="📥 Download Stego Video",
                            data=stego_video_bytes,
                            file_name="stego_video.mp4",
                            mime="video/mp4"
                        )
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please provide both cover video and secret message")
    
    else:  # Decode
        st.subheader("Extract Hidden Data")
        stego_video = st.file_uploader("Upload stego video:", type=['mp4', 'avi'], key="vid_stego")
        password = st.text_input("Password (if used):", type="password", key="vid_dec_pass")
        
        if st.button("🔓 Extract Hidden Data", type="primary"):
            if stego_video:
                try:
                    with st.spinner("Extracting data from video..."):
                        temp_path = save_uploaded_file(stego_video)
                        pwd = password if password else None
                        secret_data = VideoSteganography.decode(temp_path, pwd)
                        os.unlink(temp_path)
                    
                    st.success("✅ Data extracted successfully!")
                    secret_text = secret_data.decode('utf-8')
                    st.text_area("Extracted Secret Message:", value=secret_text, height=200)
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please upload a stego video") """


# ========== TEXT STEGANOGRAPHY ==========
elif stego_type == "Text":
    st.header("📝 Text Steganography")
    st.markdown("Hide secret data in plain text using zero-width characters")
    
    if mode == "Encode (Hide)":
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Cover Text")
            cover_text = st.text_area("Enter cover text:", height=200, 
                                     placeholder="Enter some normal text that will contain hidden data...")
            
            if cover_text:
                capacity = TextSteganography.get_capacity(cover_text)
                st.info(f"📊 Estimated capacity: ~{capacity} bytes")
        
        with col2:
            st.subheader("Secret Message")
            secret_text = st.text_area("Enter secret message:", height=150, key="txt_secret")
            password = st.text_input("Password (optional):", type="password", key="txt_enc_pass")
            
            if st.button("🔒 Hide Data in Text", type="primary"):
                if cover_text and secret_text:
                    try:
                        secret_data = secret_text.encode('utf-8')
                        pwd = password if password else None
                        stego_text = TextSteganography.encode(cover_text, secret_data, pwd)
                        
                        st.success("✅ Data hidden successfully!")
                        st.text_area("Stego Text (copy this):", value=stego_text, height=200)
                        
                        st.info("ℹ️ The text looks identical but contains hidden zero-width characters!")
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please provide both cover text and secret message")
    
    else:  # Decode
        st.subheader("Extract Hidden Data")
        stego_text = st.text_area("Paste stego text:", height=200, key="txt_stego")
        password = st.text_input("Password (if used):", type="password", key="txt_dec_pass")
        
        if st.button("🔓 Extract Hidden Data", type="primary"):
            if stego_text:
                try:
                    pwd = password if password else None
                    secret_data = TextSteganography.decode(stego_text, pwd)
                    
                    st.success("✅ Data extracted successfully!")
                    secret_text = secret_data.decode('utf-8')
                    st.text_area("Extracted Secret Message:", value=secret_text, height=200)
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please paste the stego text")


# ========== FILE IN IMAGE STEGANOGRAPHY ==========
elif stego_type == "File in Image":
    st.header("📄 File in Image Steganography")
    st.markdown("Hide any file type inside an image")
    
    if mode == "Encode (Hide)":
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Cover Image")
            cover_image = st.file_uploader("Upload cover image", type=['png', 'bmp'], key="file_img_cover")
            
            if cover_image:
                img = Image.open(cover_image)
                st.image(img, caption="Cover Image", use_container_width=True)
                
                temp_path = save_uploaded_file(cover_image)
                capacity = ImageSteganography.get_capacity(temp_path)
                st.success(f"✅ Capacity: {capacity:,} bytes ({capacity/1024:.2f} KB)")
                os.unlink(temp_path)
        
        with col2:
            st.subheader("Secret File")
            secret_file = st.file_uploader("Upload file to hide:", type=None, key="secret_file")
            password = st.text_input("Password (optional):", type="password", key="file_enc_pass")
            
            if st.button("🔒 Hide File in Image", type="primary"):
                if cover_image and secret_file:
                    try:
                        temp_img_path = save_uploaded_file(cover_image)
                        file_data = secret_file.read()
                        
                        pwd = password if password else None
                        stego_image_bytes = FileFolderSteganography.encode_file(
                            temp_img_path, file_data, secret_file.name, pwd
                        )
                        os.unlink(temp_img_path)
                        
                        st.success(f"✅ File '{secret_file.name}' hidden successfully!")
                        
                        stego_img = Image.open(io.BytesIO(stego_image_bytes))
                        st.image(stego_img, caption="Stego Image", use_container_width=True)
                        
                        st.download_button(
                            label="📥 Download Stego Image",
                            data=stego_image_bytes,
                            file_name="stego_image_with_file.png",
                            mime="image/png"
                        )
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please provide both cover image and secret file")
    
    else:  # Decode
        st.subheader("Extract Hidden File")
        stego_image = st.file_uploader("Upload stego image:", type=['png', 'bmp'], key="file_img_stego")
        password = st.text_input("Password (if used):", type="password", key="file_dec_pass")
        
        if st.button("🔓 Extract Hidden File", type="primary"):
            if stego_image:
                try:
                    temp_path = save_uploaded_file(stego_image)
                    pwd = password if password else None
                    filename, file_data = FileFolderSteganography.decode_file(temp_path, pwd)
                    os.unlink(temp_path)
                    
                    st.success(f"✅ File extracted: {filename}")
                    st.download_button(
                        label=f"📥 Download {filename}",
                        data=file_data,
                        file_name=filename
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please upload a stego image")


# ========== FOLDER IN IMAGE STEGANOGRAPHY ==========
elif stego_type == "Folder in Image":
    st.header("📁 Folder in Image Steganography")
    st.markdown("Hide multiple files inside an image")
    
    if mode == "Encode (Hide)":
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Cover Image")
            cover_image = st.file_uploader("Upload cover image", type=['png', 'bmp'], key="folder_img_cover")
            
            if cover_image:
                img = Image.open(cover_image)
                st.image(img, caption="Cover Image", use_container_width=True)
                
                temp_path = save_uploaded_file(cover_image)
                capacity = ImageSteganography.get_capacity(temp_path)
                st.success(f"✅ Capacity: {capacity:,} bytes ({capacity/1024:.2f} KB)")
                os.unlink(temp_path)
        
        with col2:
            st.subheader("Files to Hide")
            secret_files = st.file_uploader("Upload multiple files:", accept_multiple_files=True, key="secret_files")
            password = st.text_input("Password (optional):", type="password", key="folder_enc_pass")
            
            if secret_files:
                st.info(f"📦 {len(secret_files)} file(s) selected")
            
            if st.button("🔒 Hide Files in Image", type="primary"):
                if cover_image and secret_files:
                    try:
                        temp_img_path = save_uploaded_file(cover_image)
                        
                        # Prepare folder files dict
                        folder_files = {}
                        for f in secret_files:
                            folder_files[f.name] = f.read()
                        
                        pwd = password if password else None
                        stego_image_bytes = FileFolderSteganography.encode_folder(
                            temp_img_path, folder_files, pwd
                        )
                        os.unlink(temp_img_path)
                        
                        st.success(f"✅ {len(secret_files)} file(s) hidden successfully!")
                        
                        stego_img = Image.open(io.BytesIO(stego_image_bytes))
                        st.image(stego_img, caption="Stego Image", use_container_width=True)
                        
                        st.download_button(
                            label="📥 Download Stego Image",
                            data=stego_image_bytes,
                            file_name="stego_image_with_folder.png",
                            mime="image/png"
                        )
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please provide cover image and files to hide")
    
    else:  # Decode
        st.subheader("Extract Hidden Files")
        stego_image = st.file_uploader("Upload stego image:", type=['png', 'bmp'], key="folder_img_stego")
        password = st.text_input("Password (if used):", type="password", key="folder_dec_pass")
        
        if st.button("🔓 Extract Hidden Files", type="primary"):
            if stego_image:
                try:
                    temp_path = save_uploaded_file(stego_image)
                    pwd = password if password else None
                    folder_files = FileFolderSteganography.decode_folder(temp_path, pwd)
                    os.unlink(temp_path)
                    
                    st.success(f"✅ {len(folder_files)} file(s) extracted!")
                    
                    for filename, file_data in folder_files.items():
                        st.download_button(
                            label=f"📥 Download {filename}",
                            data=file_data,
                            file_name=filename,
                            key=f"dl_{filename}"
                        )
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please upload a stego image")


# ========== NETWORK STEGANOGRAPHY ==========
elif stego_type == "Network Packets":
    st.header("📡 Network Packet Steganography")
    st.markdown("Hide data in network packet headers (TCP/IP)")
    
    method = st.radio("Select Method:", ["TCP Sequence Numbers", "IP Identification Field"])
    
    if mode == "Encode (Hide)":
        st.subheader("Create Stego Packets")
        
        secret_text = st.text_area("Enter secret message:", height=150, key="net_secret")
        password = st.text_input("Password (optional):", type="password", key="net_enc_pass")
        
        col1, col2 = st.columns(2)
        with col1:
            dest_ip = st.text_input("Destination IP:", value="192.168.1.1")
        with col2:
            if method == "TCP Sequence Numbers":
                dest_port = st.number_input("Destination Port:", value=80, min_value=1, max_value=65535)
        
        if st.button("🔒 Create Stego Packets", type="primary"):
            if secret_text:
                try:
                    secret_data = secret_text.encode('utf-8')
                    pwd = password if password else None
                    
                    if method == "TCP Sequence Numbers":
                        pcap_data = NetworkSteganography.encode_tcp_isn(secret_data, pwd, dest_ip, dest_port)
                    else:
                        pcap_data = NetworkSteganography.encode_ip_id(secret_data, pwd, dest_ip)
                    
                    st.success("✅ Stego packets created!")
                    st.download_button(
                        label="📥 Download PCAP File",
                        data=pcap_data,
                        file_name="stego_packets.pcap",
                        mime="application/vnd.tcpdump.pcap"
                    )
                    
                    st.info("ℹ️ Download this PCAP file and analyze it with Wireshark or similar tools")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please enter a secret message")
    
    else:  # Decode
        st.subheader("Extract Data from Packets")
        pcap_file = st.file_uploader("Upload PCAP file:", type=['pcap'], key="net_pcap")
        password = st.text_input("Password (if used):", type="password", key="net_dec_pass")
        
        if st.button("🔓 Extract Hidden Data", type="primary"):
            if pcap_file:
                try:
                    pcap_data = pcap_file.read()
                    pwd = password if password else None
                    
                    if method == "TCP Sequence Numbers":
                        secret_data = NetworkSteganography.decode_tcp_isn(pcap_data, pwd)
                    else:
                        secret_data = NetworkSteganography.decode_ip_id(pcap_data, pwd)
                    
                    st.success("✅ Data extracted successfully!")
                    secret_text = secret_data.decode('utf-8')
                    st.text_area("Extracted Secret Message:", value=secret_text, height=200)
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please upload a PCAP file")


# ========== EMOJI STEGANOGRAPHY ==========
elif stego_type == "Emoji":
    st.header("😀 Emoji Steganography")
    st.markdown("Hide secret data as emoji sequences")
    
    if mode == "Encode (Hide)":
        st.subheader("Convert Secret to Emojis")
        
        secret_text = st.text_area("Enter secret message:", height=150, key="emoji_secret")
        password = st.text_input("Password (optional):", type="password", key="emoji_enc_pass")
        bits_per_emoji = st.radio("Encoding density:", [2, 3], 
                                  help="2 bits = 4 emojis, 3 bits = 8 emojis")
        
        if st.button("🔒 Convert to Emojis", type="primary"):
            if secret_text:
                try:
                    secret_data = secret_text.encode('utf-8')
                    pwd = password if password else None
                    emoji_string = EmojiSteganography.encode(secret_data, pwd, bits_per_emoji)
                    
                    st.success("✅ Data encoded as emojis!")
                    st.text_area("Emoji String (copy this):", value=emoji_string, height=200)
                    
                    st.info(f"ℹ️ {len(emoji_string)} characters (including {emoji_string.count('😀') + emoji_string.count('🎉')} emojis)")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please enter a secret message")
    
    else:  # Decode
        st.subheader("Decode Emojis to Secret")
        
        emoji_string = st.text_area("Paste emoji string:", height=150, key="emoji_stego")
        password = st.text_input("Password (if used):", type="password", key="emoji_dec_pass")
        bits_per_emoji = st.radio("Encoding density used:", [2, 3])
        
        if st.button("🔓 Decode Emojis", type="primary"):
            if emoji_string:
                try:
                    pwd = password if password else None
                    secret_data = EmojiSteganography.decode(emoji_string, pwd, bits_per_emoji)
                    
                    st.success("✅ Data decoded successfully!")
                    secret_text = secret_data.decode('utf-8')
                    st.text_area("Extracted Secret Message:", value=secret_text, height=200)
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Please paste the emoji string")


# Footer
st.markdown("---")
st.markdown("""
### 📚 About Steganography
Steganography is the practice of hiding secret information within an ordinary file or message to avoid detection.
This tool supports multiple methods:
- **Image**: LSB (Least Significant Bit) technique
- **Audio**: LSB in audio samples
- **Video**: Frame-based LSB embedding
- **Text**: Zero-width characters
- **Files/Folders**: Compression + image hiding
- **Network**: Packet header manipulation
- **Emoji**: Data encoding as emoji sequences

**Security Tip**: Always use a strong password for sensitive data!
""")
