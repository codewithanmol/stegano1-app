import io
import zipfile


def zip_bytes_from_paths(paths):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p, data in paths:
            # path should be a relative filename
            z.writestr(p, data)
    return buf.getvalue()


def unzip_bytes_to_dict(b):
    buf = io.BytesIO(b)
    out = {}
    with zipfile.ZipFile(buf, "r") as z:
        for name in z.namelist():
            out[name] = z.read(name)
    return out
