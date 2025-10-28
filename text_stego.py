# zero-width based text steganography
ZW0 = '\u200b'  # zero width space -> bit 1
ZW1 = '\u200c'  # zero width non-joiner -> bit 0


def _to_bits(s: bytes):
    for b in s:
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


def hide_text_in_text(cover: str, secret: str) -> str:
    sb = secret.encode('utf-8')
    bits = list(_to_bits(sb))
    # append marker
    marker = b"STXT1\x00"
    bits = list(_to_bits(marker)) + bits
    # put zero-width chars at the end of cover
    zw = ''.join(ZW0 if bit else ZW1 for bit in bits)
    return cover + zw


def extract_text_from_text(stego: str) -> str:
    # read zero-width block from end
    zw_chars = ''.join(ch for ch in stego if ch in (ZW0, ZW1))
    bits = [1 if ch == ZW0 else 0 for ch in zw_chars]
    data = _bits_to_bytes(bits)
    idx = data.find(b"STXT1\x00")
    if idx == -1:
        raise ValueError("Marker not found")
    payload = data[idx+6:]
    return payload.decode('utf-8', errors='ignore')
