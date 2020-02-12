from typing import List

from core.db.db import Session
from core.db.models import QRCodeCoupon
from core.services.parser import parse_coupon_date, parse_coupon_number
from core.services.qr import get_cropped_image
from sqlalchemy import func, asc
from PIL import Image


def save_coupons(original_image: Image.Image, user_id: int, qr_codes: List):
    session = Session()

    existed = []
    for num, qr in enumerate(qr_codes):
        # cut single coupon
        croped_img = get_cropped_image(original_image, qr)

        # parse data from image
        expiry_date = parse_coupon_date(croped_img)
        coupon_number = parse_coupon_number(qr.data)

        exist = is_coupon_by_number_exist(user_id, coupon_number)
        if not exist:
            # add file info to DB
            file_md = QRCodeCoupon(user_id, qr.data, coupon_number, expiry_date)
            session.add(file_md)
        else:
            existed.append(coupon_number)

    session.commit()
    session.close()
    return existed


def get_unused_coupons(user_id: int):
    session = Session()
    coupons = session.query(QRCodeCoupon).filter_by(user_id=user_id, used=False).order_by(
        asc(QRCodeCoupon.expiry_date)).all()
    session.close()

    return coupons


def get_unused_coupon(user_id: int):
    session = Session()
    qr_coupon = session.query(QRCodeCoupon).filter_by(user_id=user_id, used=False).order_by(
        asc(QRCodeCoupon.expiry_date)).first()
    session.close()

    return qr_coupon


def is_coupon_by_number_exist(user_id: int, coupon_number: str):
    session = Session()
    instance = session.query(QRCodeCoupon).filter_by(user_id=user_id, coupon_number=coupon_number).first()
    session.close()

    return True if instance else False


def mark_coupon(user_id: int, coupon_number: str, mark: bool):
    session = Session()
    qr_coupon = session.query(QRCodeCoupon).filter_by(user_id=user_id, coupon_number=coupon_number).first()
    qr_coupon.used = mark
    session.add(qr_coupon)
    session.commit()
    session.close()


def get_coupon_obj(user_id: int, coupon_number: str):
    session = Session()
    qr_coupon = session.query(QRCodeCoupon).filter_by(user_id=user_id, coupon_number=coupon_number).first()
    session.close()

    return qr_coupon


def get_summary_by_expire_date(user_id: int):
    session = Session()
    summary = session.query(func.count(QRCodeCoupon.user_id), QRCodeCoupon.expiry_date, QRCodeCoupon.used).filter_by(
        user_id=user_id, used=False).group_by(
        QRCodeCoupon.user_id, QRCodeCoupon.expiry_date, QRCodeCoupon.used).all()
    session.close()

    return summary


def get_summary_message(user_id: int):
    summary_info = get_summary_by_expire_date(user_id)
    if len(summary_info):
        sum_info = '\n'.join([f'{q[0]} талонов сроком до {q[1].strftime("%d/%m/%Y") if q[1] else "<u>Неизвестно</u>"}' for q in summary_info])
        return f'Доступно: \n{sum_info}'
    else:
        return 'Нет доступных талонов.\n' \
               'Загрузите новые талоны прикрепив файл.'
