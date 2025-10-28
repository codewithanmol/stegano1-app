import streamlit as st
from pathlib import Path
import io
import base64

from stego import image_stego, text_stego, audio_stego, video_stego, emoji_stego, network_stego, utils

st.set_page_config(page_title='StegoHub', layout='wide')

st.title('StegoHub — Multi-mode Steganography Demo')

mode = st.sidebar.selectbox('Mode', ['Image', 'Text', 'Audio', 'Video', 'Emoji', 'Network', 'Folder/File'])

if mode == 'Image':
    st.header('Image (PNG) LSB Steganography')
    uploaded = st.file_uploader('Upload PNG cover image', type=['png'])
    secret_text = st.text_area('Secret text (optional)')
    secret_file = st.file_uploader('Or secret file to hide (optional)')
    col1, col2 = st.columns(2)
    if st.button('Embed'):
        if not uploaded:
            st.error('Upload a PNG cover image')
        else:
            cover = uploaded.read()
            if secret_file:
                payload = secret_file.read()
            else:
                payload = secret_text.encode('utf-8')
            try:
                out = image_stego.hide_bytes_in_png(cover, payload)
                st.success('Embedded payload')
                st.download_button('Download stego PNG', data=out, file_name='stego.png', mime='image/png')
            except Exception as e:
                st.error(str(e))
    st.markdown('---')
    st.subheader('Extract')
    uploaded2 = st.file_uploader('Upload stego PNG to extract', type=['png'], key='ext_img')
    if st.button('Extract', key='extract_img'):
        if not uploaded2:
            st.error('Upload a stego PNG')
        else:
            try:
                data = image_stego.extract_bytes_from_png(uploaded2.read())
                st.success('Extraction complete')
                st.download_button('Download extracted payload', data=data, file_name='extracted.bin')
                try:
                    text = data.decode('utf-8')
                    st.code(text)
                except Exception:
                    pass
            except Exception as e:
                st.error(str(e))

elif mode == 'Text':
    st.header('Text zero-width Steganography')
    cover = st.text_area('Cover text')
    secret = st.text_area('Secret text to hide')
    if st.button('Embed text'):
        if not cover:
            st.error('Provide cover text')
        else:
            out = text_stego.hide_text_in_text(cover, secret)
            st.success('Hidden text inside cover (zero-width chars appended)')
            st.download_button('Download stego text', data=out, file_name='stego.txt', mime='text/plain')
    st.markdown('---')
    stego_text = st.text_area('Paste stego text to extract')
    if st.button('Extract text'):
        try:
            out = text_stego.extract_text_from_text(stego_text)
            st.success('Extracted')
            st.code(out)
        except Exception as e:
            st.error(str(e))

elif mode == 'Audio':
    st.header('Audio (WAV) LSB Steganography')
    uploaded = st.file_uploader('Upload WAV cover audio', type=['wav'])
    secret_text = st.text_area('Secret text (optional)')
    secret_file = st.file_uploader('Or secret file to hide (optional)', key='audfile')
    if st.button('Embed'):
        if not uploaded:
            st.error('Upload WAV cover')
        else:
            cover = uploaded.read()
            if secret_file:
                payload = secret_file.read()
            else:
                payload = secret_text.encode('utf-8')
            try:
                out = audio_stego.hide_bytes_in_wav(cover, payload)
                st.success('Embedded payload in WAV')
                st.download_button('Download stego WAV', data=out, file_name='stego.wav', mime='audio/wav')
            except Exception as e:
                st.error(str(e))
    st.markdown('---')
    st.subheader('Extract')
    uploaded2 = st.file_uploader('Upload stego WAV to extract', type=['wav'], key='ext_wav')
    if st.button('Extract WAV', key='extract_wav'):
        if not uploaded2:
            st.error('Upload a stego WAV')
        else:
            try:
                data = audio_stego.extract_bytes_from_wav(uploaded2.read())
                st.success('Extraction complete')
                st.download_button('Download extracted payload', data=data, file_name='extracted.bin')
                try:
                    text = data.decode('utf-8')
                    st.code(text)
                except Exception:
                    pass
            except Exception as e:
                st.error(str(e))

elif mode == 'Video':
    st.header('Video (Append marker) Steganography')
    uploaded = st.file_uploader('Upload video file (mp4 suggested)', type=['mp4','mov','mkv'])
    secret_file = st.file_uploader('Secret file to hide', key='vidsecret')
    secret_text = st.text_area('Or secret text to hide')
    if st.button('Embed'):
        if not uploaded:
            st.error('Upload a video file')
        else:
            video = uploaded.read()
            if secret_file:
                payload = secret_file.read()
            else:
                payload = secret_text.encode('utf-8')
            try:
                out = video_stego.hide_bytes_in_video(video, payload)
                st.success('Embedded payload (appended)')
                st.download_button('Download stego video', data=out, file_name='stego_video'+Path(uploaded.name).suffix, mime='video/mp4')
            except Exception as e:
                st.error(str(e))
    st.markdown('---')
    uploaded2 = st.file_uploader('Upload stego video to extract', type=['mp4','mov','mkv'], key='ext_vid')
    if st.button('Extract video payload'):
        if not uploaded2:
            st.error('Upload stego video')
        else:
            try:
                data = video_stego.extract_bytes_from_video(uploaded2.read())
                st.success('Extraction complete')
                st.download_button('Download extracted payload', data=data, file_name='extracted.bin')
                try:
                    st.code(data.decode('utf-8'))
                except Exception:
                    pass
            except Exception as e:
                st.error(str(e))

elif mode == 'Emoji':
    st.header('Emoji Steganography')
    secret = st.text_area('Secret text to hide')
    if st.button('Encode as emoji'):
        out = emoji_stego.hide_text_as_emoji(secret)
        st.success('Encoded')
        st.code(out)
        st.download_button('Download emoji text', data=out, file_name='emoji.txt')
    st.markdown('---')
    emoji_input = st.text_area('Paste emoji string to extract')
    if st.button('Extract emoji text'):
        try:
            out = emoji_stego.extract_text_from_emoji(emoji_input)
            st.success('Extracted')
            st.code(out)
        except Exception as e:
            st.error(str(e))

elif mode == 'Network':
    st.header('Network (simulated) Steganography')
    secret_file = st.file_uploader('Secret file to hide', key='netsecret')
    secret_text = st.text_area('Or secret text to hide')
    if st.button('Export simulated DNS queries'):
        if secret_file:
            payload = secret_file.read()
        else:
            payload = secret_text.encode('utf-8')
        out = network_stego.payload_to_fake_dns_lines(payload)
        st.download_button('Download fake DNS queries', data=out, file_name='dns_queries.txt')
    st.markdown('---')
    net_input = st.text_area('Paste fake DNS file contents to extract')
    if st.button('Extract from fake DNS'):
        try:
            out = network_stego.extract_payload_from_fake_dns_file(net_input)
            st.success('Extracted')
            st.download_button('Download extracted payload', data=out, file_name='extracted.bin')
            try:
                st.code(out.decode('utf-8'))
            except Exception:
                pass
        except Exception as e:
            st.error(str(e))

elif mode == 'Folder/File':
    st.header('Zip folder/file and embed in chosen carrier')
    st.write('Upload files to include in zip:')
    files = st.file_uploader('Files (multiple)', accept_multiple_files=True)
    carrier = st.selectbox('Carrier type', ['Image','Audio','Video','Text'])
    cover = st.file_uploader('Cover file (depends on carrier)', key='carrier_cover')
    if st.button('Embed zip into carrier'):
        if not files:
            st.error('Upload at least one file')
        elif not cover:
            st.error('Upload a cover file for the chosen carrier')
        else:
            pairs = [(f.name, f.read()) for f in files]
            zipped = utils.zip_bytes_from_paths(pairs)
            try:
                if carrier == 'Image':
                    out = image_stego.hide_bytes_in_png(cover.read(), zipped)
                    st.download_button('Download stego image', data=out, file_name='stego.png', mime='image/png')
                elif carrier == 'Audio':
                    out = audio_stego.hide_bytes_in_wav(cover.read(), zipped)
                    st.download_button('Download stego wav', data=out, file_name='stego.wav', mime='audio/wav')
                elif carrier == 'Video':
                    out = video_stego.hide_bytes_in_video(cover.read(), zipped)
                    st.download_button('Download stego video', data=out, file_name='stego_video'+Path(cover.name).suffix)
                elif carrier == 'Text':
                    # embed as zero-width appended to text file
                    cover_text = cover.read().decode('utf-8')
                    out_text = text_stego.hide_text_in_text(cover_text, zipped.decode('latin1'))
                    st.download_button('Download stego text', data=out_text, file_name='stego.txt')
                st.success('Embedded zipped payload')
            except Exception as e:
                st.error(str(e))

    st.markdown('---')
    st.subheader('Extract zip from carrier')
    carrier2 = st.selectbox('Carrier type (extract)', ['Image','Audio','Video','Text'], key='carrier_extract')
    cover2 = st.file_uploader('Upload stego carrier file', key='carrier_cover2')
    if st.button('Extract zip'):
        if not cover2:
            st.error('Upload carrier')
        else:
            try:
                if carrier2 == 'Image':
                    data = image_stego.extract_bytes_from_png(cover2.read())
                elif carrier2 == 'Audio':
                    data = audio_stego.extract_bytes_from_wav(cover2.read())
                elif carrier2 == 'Video':
                    data = video_stego.extract_bytes_from_video(cover2.read())
                elif carrier2 == 'Text':
                    txt = cover2.read().decode('utf-8')
                    data = text_stego.extract_text_from_text(txt).encode('latin1')
                st.download_button('Download extracted zip payload', data=data, file_name='extracted.zip')
                st.success('Extraction complete')
            except Exception as e:
                st.error(str(e))
