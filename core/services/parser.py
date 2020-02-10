import re
from datetime import date
from PIL import Image
import pytesseract


def _parse_expiry_date(text: str) -> date:
    expiry_date = None

    result = re.search(r'(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})', text)

    if result:
        expiry_date = date(
            int(result.group('year')),
            int(result.group('month')),
            int(result.group('day'))
        )

    return expiry_date


def parse_coupon_date(img: Image.Image):
    # Resize image before parsing text from it
    img = img.resize((img.size[0]*2, img.size[1]*2))
    # Parse text from image
    text = pytesseract.image_to_string(img, lang='ukr')

    expiry_date = _parse_expiry_date(text)

    return expiry_date


def parse_coupon_number(data: bytes):
    qr_string = data.decode('utf-8')
    result = re.search(r';(?P<number>\d{20})=', qr_string)
    return result.group('number') if result else None
