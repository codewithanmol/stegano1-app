from PIL import Image
import numpy as np
import io

MARKER = b"STEGO-IMG-1\x00"


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


def hide_bytes_in_png(png_bytes: bytes, payload: bytes) -> bytes:
    im = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    arr = np.array(im)
    h, w, c = arr.shape
    capacity = h * w * 3  # use RGB channels LSB
    data = MARKER + len(payload).to_bytes(8, "big") + payload
    bits = list(_to_bits(data))
    if len(bits) > capacity:
        raise ValueError("Payload too large for cover image")
    flat = arr.reshape(-1, 4)
    bit_iter = iter(bits)
    for i in range(len(flat)):
        for ch in range(3):
            try:
                bit = next(bit_iter)
            except StopIteration:
                break
            # ensure uint8-safe operations: mask with 0xFE then or the bit
            flat[i][ch] = (int(flat[i][ch]) & 0xFE) | int(bit)
        else:
            continue
        break
    new = Image.fromarray(arr)
    out = io.BytesIO()
    new.save(out, format="PNG")
    return out.getvalue()


def extract_bytes_from_png(png_bytes: bytes) -> bytes:
    im = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    arr = np.array(im)
    flat = arr.reshape(-1, 4)
    bits = []
    for pix in flat:
        for ch in range(3):
            bits.append(int(pix[ch]) & 1)
    data = _bits_to_bytes(bits)
    # find marker
    idx = data.find(MARKER)
    if idx == -1:
        raise ValueError("Marker not found")
    idx += len(MARKER)
    size = int.from_bytes(data[idx:idx+8], "big")
    idx += 8
    payload = data[idx:idx+size]
    return payload


def hide_text_in_image(png_bytes: bytes, text: str) -> bytes:
    return hide_bytes_in_png(png_bytes, text.encode('utf-8'))


def extract_text_from_image(png_bytes: bytes) -> str:
    return extract_bytes_from_png(png_bytes).decode('utf-8', errors='ignore')
