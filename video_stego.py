# Simple append-with-marker video stego (not robust but easy to demo)
MARKER = b"STEGO-VID-1\x00"


def hide_bytes_in_video(video_bytes: bytes, payload: bytes) -> bytes:
    return video_bytes + MARKER + len(payload).to_bytes(8, 'big') + payload


def extract_bytes_from_video(video_bytes: bytes) -> bytes:
    idx = video_bytes.find(MARKER)
    if idx == -1:
        raise ValueError('Marker not found')
    idx += len(MARKER)
    size = int.from_bytes(video_bytes[idx:idx+8], 'big')
    idx += 8
    payload = video_bytes[idx:idx+size]
    return payload
