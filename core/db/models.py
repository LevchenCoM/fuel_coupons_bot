import datetime

from sqlalchemy import Column, String, Integer, DateTime, Date, Boolean, Binary
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class QRCodeCoupon(Base):
    __tablename__ = 'qr_code_coupons'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    qr_bytes = Column(Binary)
    coupon_number = Column(String)
    expiry_date = Column(Date)
    used = Column(Boolean)
    last_sent = Column(DateTime)
    created = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, user_id, qr_bytes, coupon_number, expiry_date, used=False, last_sent=None):
        self.user_id = user_id
        self.qr_bytes = qr_bytes
        self.coupon_number = coupon_number
        self.expiry_date = expiry_date
        self.used = used
        self.last_sent = last_sent


