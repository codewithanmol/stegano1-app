from PIL import Image
import io
import numpy as np
from stego import image_stego, text_stego


def make_sample_png(w=64, h=64):
    import numpy as np
    arr = np.random.randint(0, 255, (h, w, 4), dtype=np.uint8)
    from PIL import Image
    im = Image.fromarray(arr)
    buf = io.BytesIO()
    im.save(buf, format='PNG')
    return buf.getvalue()


def test_image():
    cover = make_sample_png()
    secret = b'Hello Stego Test!'
    out = image_stego.hide_bytes_in_png(cover, secret)
    rec = image_stego.extract_bytes_from_png(out)
    assert rec == secret, f"Image extraction mismatch: {rec} != {secret}"
    print('Image stego PASS')


def test_text():
    cover = 'This is cover text.'
    secret = 'hidden message'
    stego = text_stego.hide_text_in_text(cover, secret)
    ext = text_stego.extract_text_from_text(stego)
    assert ext == secret, f"Text extraction mismatch: {ext} != {secret}"
    print('Text stego PASS')

if __name__ == '__main__':
    test_text()
    test_image()
    print('All tests passed')
