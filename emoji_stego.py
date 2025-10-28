# Map bits to emoji pairs
ZERO_EMOJI = '🙂'  # encodes 0
ONE_EMOJI = '😎'   # encodes 1
MARKER = '\u2744'  # snowflake as marker


def hide_text_as_emoji(text: str) -> str:
    b = text.encode('utf-8')
    bits = []
    for byte in b:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
    ems = ''.join(ONE_EMOJI if bit else ZERO_EMOJI for bit in bits)
    return MARKER + ems


def extract_text_from_emoji(emoji_str: str) -> str:
    idx = emoji_str.find(MARKER)
    if idx == -1:
        raise ValueError('Marker not found')
    ems = emoji_str[idx+len(MARKER):]
    bits = []
    for ch in ems:
        if ch == ONE_EMOJI:
            bits.append(1)
        elif ch == ZERO_EMOJI:
            bits.append(0)
        else:
            # ignore other chars
            pass
    # convert bits to bytes
    b = bytearray()
    cur = 0
    for i, bit in enumerate(bits):
        cur = (cur << 1) | bit
        if (i % 8) == 7:
            b.append(cur & 0xFF)
            cur = 0
    return bytes(b).decode('utf-8', errors='ignore')
