from io import BytesIO

import pyqrcode
from typing import List, ByteString
from pyzbar.pyzbar import decode, Decoded
from PIL import Image


def get_all_qr_codes(img: Image.Image) -> List[Decoded]:
    codes = decode(img)

    return codes


def create_png(string: ByteString):
    qr_code = pyqrcode.create(string)
    bi = BytesIO()
    qr_code.png(bi, scale=32)
    return bi


def get_cropped_image(original_image: Image.Image, qr) -> Image.Image:
    u_left, b_left, b_right, u_right = qr.polygon[0], qr.polygon[1], qr.polygon[2], qr.polygon[3],
    height = qr.rect.height
    width = qr.rect.width

    left = u_right.x
    top = u_left.y - 10
    right = u_right.x + width * 2
    bottom = int(u_left.y + height / 3)

    return original_image.crop((left, top, right, bottom))
