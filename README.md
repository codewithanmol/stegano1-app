# Steganography Streamlit App

This project is a multi-mode steganography demo implemented as a Streamlit web app. It supports multiple hiding/extraction methods:

- Image (LSB PNG) — hide/extract text or files in images
- Text (zero-width characters) — hide/extract text inside cover text
- Audio (WAV LSB) — hide/extract text/files inside WAV files
- Video (append-with-marker) — add/extract payload appended to container (simple method)
- Emoji — encode text as emoji sequences
- Network (simulated) — split payload into fake DNS-like labels saved to file
- Folder/File — zip and embed using one of the carriers

This is a minimal, educational implementation. It focuses on clarity and portability.

How to run

1. Create a virtual environment and install dependencies (Windows PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate; pip install -r requirements.txt
```

2. Run the Streamlit app:

```powershell
streamlit run app.py
```

Notes and limitations

- Image stego uses LSB on PNG images (lossless). Avoid JPEG.
- Audio stego supports PCM WAV files only.
- Video stego uses a simple append-with-marker approach; it's not robust but easy to demo.
- Network stego is a simulated exporter (creates a text file of DNS-like queries).

Files

- `app.py` — Streamlit UI and wiring
- `stego/*.py` — implementation modules

Next steps

- Add tests and more robust video/audio handling (ffmpeg-based frame embedding)
- Secure payload encryption before embedding
- Add progress indicators for large files

Enjoy — use responsibly and ethically.