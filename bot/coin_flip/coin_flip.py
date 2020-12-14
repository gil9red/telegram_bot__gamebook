#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import random
import re
from pathlib import Path

# pip install python-telegram-bot
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
)
from telegram.ext import Updater, CallbackQueryHandler, CallbackContext

from bot import text as text_of
from bot.common import log, log_func, get_button_delete_message
from bot.regexp import fill_string_pattern


CURRENT_DIR = Path(__file__).resolve().parent
PATTERN_COIN_FLIP = re.compile(r'^coin_flip$')


def get_button_coin_flip(text: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text, callback_data=fill_string_pattern(PATTERN_COIN_FLIP))


COIN_VARIANTS = {
    'орел': CURRENT_DIR / 'images' / 'орел_512x512.png',
    'решка': CURRENT_DIR / 'images' / 'решка_512x512.png',
}


@log_func(log)
def on_callback_coin_flip(update: Update, context: CallbackContext):
    message = update.effective_message

    query = update.callback_query
    query.answer()

    reply_markup = InlineKeyboardMarkup.from_row([
        get_button_coin_flip(text_of.BTN_COIN_FLIP_REPEAT),
        get_button_delete_message(text_of.BTN_COIN_FLIP_HIDE),
    ])

    value = random.choice(list(COIN_VARIANTS))
    f = open(COIN_VARIANTS[value], 'rb')

    is_new = not message.photo
    if is_new:
        message.reply_photo(
            f,
            caption=f"{text_of.BTN_COIN_FLIP_RESULT}: {value}",
            reply_markup=reply_markup,
            reply_to_message_id=message.message_id
        )
    else:
        message.edit_media(
            InputMediaPhoto(f, f'{message.caption}, {value}'),
            reply_markup=reply_markup
        )


def setup(updater: Updater):
    dp = updater.dispatcher
    dp.add_handler(CallbackQueryHandler(on_callback_coin_flip, pattern=PATTERN_COIN_FLIP, run_async=True))
