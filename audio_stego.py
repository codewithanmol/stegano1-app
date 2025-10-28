import wave
import io

MARKER = b"STEGO-AUD-1\x00"


def _to_bits(data: bytes):
    for b in data:
        for i in range(8):
            yield (b >> (7 - i)) & 1


def _bits_to_bytes(bits):
    b = 0
    out = bytearray()
    for i, bit in enumerate(bits):
        b = (b << 1) | bit
        if (i % 8) == 7:
            out.append(b & 0xFF)
            b = 0
    return bytes(out)


def hide_bytes_in_wav(wav_bytes: bytes, payload: bytes) -> bytes:
    with wave.open(io.BytesIO(wav_bytes), 'rb') as r:
        params = r.getparams()
        frames = bytearray(r.readframes(r.getnframes()))
    capacity = len(frames)  # one bit per sample byte
    data = MARKER + len(payload).to_bytes(8, 'big') + payload
    bits = list(_to_bits(data))
    if len(bits) > capacity:
        raise ValueError('Payload too large for WAV')
    for i, bit in enumerate(bits):
        frames[i] = (frames[i] & ~1) | bit
    outbuf = io.BytesIO()
    with wave.open(outbuf, 'wb') as w:
        w.setparams(params)
        w.writeframes(bytes(frames))
    return outbuf.getvalue()


def extract_bytes_from_wav(wav_bytes: bytes) -> bytes:
    with wave.open(io.BytesIO(wav_bytes), 'rb') as r:
        frames = bytearray(r.readframes(r.getnframes()))
    bits = [b & 1 for b in frames]
    data = _bits_to_bytes(bits)
    idx = data.find(MARKER)
    if idx == -1:
        raise ValueError('Marker not found')
    idx += len(MARKER)
    size = int.from_bytes(data[idx:idx+8], 'big')
    idx += 8
    payload = data[idx:idx+size]
    return payload


def hide_text_in_wav(wav_bytes: bytes, text: str) -> bytes:
    return hide_bytes_in_wav(wav_bytes, text.encode('utf-8'))


def extract_text_from_wav(wav_bytes: bytes) -> str:
    return extract_bytes_from_wav(wav_bytes).decode('utf-8', errors='ignore')
