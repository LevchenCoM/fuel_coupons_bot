import datetime
from types import FunctionType
from typing import List
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.coupons import get_unused_coupon, mark_coupon, get_coupon_obj, get_unused_coupons, get_summary_message
from core.db.db import Session
from core.db.models import QRCodeCoupon
from core.services.qr import create_png


def upload_coupons(call, bot):
    print('Executed callback "upload_coupons" | {}'.format(datetime.datetime.now()))

    bot.send_message(
        call.message.chat.id,
        'Отлично. Прикрепите изображение с талонами. Допустимые форматы: png, jpg'
    )


def get_all_coupons(call, bot):
    print('Executed callback "get_all_coupons" | {}'.format(datetime.datetime.now()))

    all_coupons = get_unused_coupons(call.message.chat.id)
    if len(all_coupons):
        for coupon in all_coupons:
            create_png_and_send(call, coupon, bot)
    else:
        bot.send_message(
            call.message.chat.id,
            'Нет доступных талонов.\n'
            'Загрузите новые талоны прикрепив файл.'
        )


def get_summary_coupons_info(call, bot):
    summary_message = get_summary_message(call.message.chat.id)
    bot.send_message(call.message.chat.id, summary_message, reply_markup=start_menu_markup)


def create_png_and_send(call, coupon: QRCodeCoupon, bot):
    png = create_png(coupon.qr_bytes)

    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(
        'Пометить использованным', callback_data=f'mark_coupon:{coupon.coupon_number}')
    )
    markup.row(InlineKeyboardButton(
        'Пометить и получить еще талон', callback_data=f'mark_coupon:{coupon.coupon_number}:next')
    )

    bot.send_photo(
        call.message.chat.id, photo=png.getvalue(), reply_markup=markup,
        caption=f'{coupon.coupon_number}\nДействителен до {coupon.expiry_date.strftime("%d/%m/%Y")}'
    )


def get_coupon(call, bot):
    print('Executed callback "get_coupon" | {}'.format(datetime.datetime.now()))
    qr_coupon = get_unused_coupon(call.message.chat.id)
    if qr_coupon:
        create_png_and_send(call, qr_coupon, bot)
    else:
        bot.send_message(call.message.chat.id, 'Нет доступных талонов')
        bot.send_message(
            call.message.chat.id, 'Выберите действие:',
            reply_markup=start_menu_markup
        )


def mark_coupon_used(call, coupon_number: str, bot, get_next=False):
    print('Executed callback "mark_coupon_used" | {}'.format(datetime.datetime.now()))

    coupon = get_coupon_obj(call.message.chat.id, coupon_number)
    already_used = coupon.used

    if already_used:
        bot.send_message(
            call.message.chat.id, f'Талон {coupon_number}\nуже помечен использованным',
            reply_markup=start_menu_markup if not get_next else None
        )
    else:
        mark_coupon(call.message.chat.id, coupon_number, mark=True)
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton(
            'Отменить пометку', callback_data=f'cancel_mark_coupon:{coupon_number}')
        )
        bot.send_message(
            call.message.chat.id, f'Талон {coupon_number}\nотмечен использованным',
            reply_markup=markup
        )

        if get_next:
            get_coupon(call, bot)
        else:
            bot.send_message(
                call.message.chat.id, 'Выберите действие:',
                reply_markup=start_menu_markup
            )


def cancel_mark_coupon_used(call, coupon_number: str, bot):
    print('Executed callback "cancel_mark_coupon_used" | {}'.format(datetime.datetime.now()))

    coupon = get_coupon_obj(call.message.chat.id, coupon_number)
    used = coupon.used

    if used:
        mark_coupon(call.message.chat.id, coupon_number, mark=False)
        bot.send_message(
            call.message.chat.id, f'Талон {coupon_number}\nотмечен неиспользованным',
            reply_markup=start_menu_markup
        )
    else:
        bot.send_message(
            call.message.chat.id, f'Невозможно отменить пометку,\nтак как талон {coupon_number}\nне использованный.',
            reply_markup=start_menu_markup
        )


MENUS = {
    'start_menu': [
        (InlineKeyboardButton('Загрузить талоны', callback_data='upload_coupons'), upload_coupons),
        (InlineKeyboardButton('Получить все доступные', callback_data='get_all_coupons'), get_all_coupons),
        (InlineKeyboardButton('Показать информацию по талонам', callback_data='get_summary'), get_summary_coupons_info),
        (InlineKeyboardButton('Получить талон', callback_data='get_coupon'), get_coupon)
    ],
    'coupon': [
        (InlineKeyboardButton('Еще талон', callback_data='next_coupon'), get_coupon),
    ]
}


def get_buttons(menu_key: str) -> List[InlineKeyboardButton]:
    menu_buttons = MENUS.get(menu_key, None)
    buttons = []
    if menu_buttons:
        buttons.extend([
            button for button, func in menu_buttons
        ])

    return buttons


def get_processing_function(button_key: str) -> FunctionType:
    function = None
    for menu_buttons in MENUS.values():
        for button, func in menu_buttons:
            if button.callback_data == button_key:
                function = func

    return function


# Start Menu
start_menu_markup = InlineKeyboardMarkup()
for button in get_buttons('start_menu'):
    start_menu_markup.row(button)

# Start Menu
coupon_markup = InlineKeyboardMarkup()
coupon_markup.row(*get_buttons('mark_coupon_used'))
