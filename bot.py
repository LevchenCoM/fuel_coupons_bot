import telebot
import traceback
import time
import menus

from io import BytesIO
from core import settings
from core.coupons import save_coupons, get_summary_message
from core.services.qr import get_all_qr_codes
from PIL import Image

from menus import mark_coupon_used, cancel_mark_coupon_used, start_menu_markup

bot = telebot.TeleBot(settings.BOT_TOKEN)


def check_access(fn):
    def wrapper(*args, **kwargs):
        message = args[0]
        if str(message.chat.id) in settings.ALLOWED_IDS:
            return fn(*args, **kwargs)
        else:
            return bot.send_message(message.chat.id, 'Упс... Доступ запрещен.')
    return wrapper


@bot.message_handler(commands=['start'])
@check_access
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, давай начнем! Выбери действие из списка',
                     reply_markup=menus.start_menu_markup)


@bot.callback_query_handler(func=lambda call: True)
def button(call):
    callback = call.data.split(':')
    if callback[0] == 'mark_coupon':
        get_next = True if len(callback) > 2 and callback[2] == 'next' else False
        mark_coupon_used(call, callback[1], bot, get_next=get_next)
    elif callback[0] == 'cancel_mark_coupon':
        cancel_mark_coupon_used(call, callback[1], bot)
    else:
        processing_func = menus.get_processing_function(call.data)
        if processing_func:
            processing_func(call, bot)


@bot.message_handler(content_types=['document'])
def file(message):
    if message.content_type == 'document':
        if message.document.mime_type in ('image/png', 'image/jpeg'):
            file_ = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_.file_path)

            bot.send_message(message.chat.id, 'Обрабатываю...')

            original_image = Image.open(BytesIO(downloaded_file))
            qr_codes = get_all_qr_codes(original_image)
            if qr_codes:
                existed_coupons = save_coupons(original_image, message.chat.id, qr_codes)
                if existed_coupons:
                    bot.send_message(message.chat.id, '\n'.join(
                        [f'Талон с номером {c} уже существует.' for c in existed_coupons]
                    ))

                summary_message = get_summary_message(message.chat.id)
                bot.send_message(message.chat.id, summary_message, reply_markup=start_menu_markup)
            else:
                bot.send_message(message.chat.id, f'В файле не найдены талоны.')
    else:
        pass


while True:
    try:
        bot.polling(none_stop=True, interval=1)
    except Exception as e:
        traceback.print_exc()
        time.sleep(1)
