# Simulated network stego exporter: split payload into DNS-like labels and save lines

MARKER = b"STEGO-NET-1\x00"


def payload_to_fake_dns_lines(payload: bytes, chunk_size=40):
    data = MARKER + len(payload).to_bytes(8, 'big') + payload
    b64 = data.hex()  # hex to keep filename-safe
    lines = [b64[i:i+chunk_size] for i in range(0, len(b64), chunk_size)]
    queries = [f"{line}.example.com" for line in lines]
    return '\n'.join(queries)


def extract_payload_from_fake_dns_file(text: str) -> bytes:
    parts = [line.split('.')[0] for line in text.splitlines() if line.strip()]
    hexstr = ''.join(parts)
    data = bytes.fromhex(hexstr)
    idx = data.find(MARKER)
    if idx == -1:
        raise ValueError('Marker not found')
    idx += len(MARKER)
    size = int.from_bytes(data[idx:idx+8], 'big')
    idx += 8
    payload = data[idx:idx+size]
    return payload
