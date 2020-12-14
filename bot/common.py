#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import functools
import logging
import sys

from itertools import tee
from pathlib import Path

from telegram import Update, InlineKeyboardButton
from telegram.ext import CallbackContext, Filters
from telegram.error import RetryAfter

from bot import text as text_of
from bot.exceptions import UnknownBookError
from bot.regexp import fill_string_pattern, PATTERN_DELETE_MESSAGE

from config import DIR_LOG, ADMIN_USERNAME


def join_page(from_page: str, page: str) -> str:
    return f'{from_page}_{page}'


# SOURCE: https://docs.python.org/3/library/itertools.html#itertools-recipes
def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def get_logger(file_name: str, dir_name='logs'):
    dir_name = Path(dir_name).resolve()
    dir_name.mkdir(parents=True, exist_ok=True)

    file_name = str(dir_name / Path(file_name).resolve().name) + '.log'

    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s] %(filename)s[LINE:%(lineno)d] %(levelname)-8s %(message)s')

    fh = logging.FileHandler(file_name, encoding='utf-8')
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.DEBUG)

    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    log.addHandler(fh)
    log.addHandler(ch)

    return log


FILTER_BY_ADMIN = Filters.user(username=ADMIN_USERNAME)


log = get_logger('log', DIR_LOG)


def get_button_delete_message(text: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text, callback_data=fill_string_pattern(PATTERN_DELETE_MESSAGE))


def log_func(log: logging.Logger):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(update: Update, context: CallbackContext):
            if update:
                chat_id = user_id = first_name = last_name = username = language_code = None

                if update.effective_chat:
                    chat_id = update.effective_chat.id

                if update.effective_user:
                    user_id = update.effective_user.id
                    first_name = update.effective_user.first_name
                    last_name = update.effective_user.last_name
                    username = update.effective_user.username
                    language_code = update.effective_user.language_code

                try:
                    message = update.effective_message.text
                except:
                    message = ''

                try:
                    query_data = update.callback_query.data
                except:
                    query_data = ''

                msg = f'[chat_id={chat_id}, user_id={user_id}, ' \
                      f'first_name={first_name!r}, last_name={last_name!r}, ' \
                      f'username={username!r}, language_code={language_code}, ' \
                      f'message={message!r}, query_data={query_data!r}]'
                msg = func.__name__ + msg

                log.debug(msg)

            return func(update, context)

        return wrapper
    return actual_decorator


def reply_error(text: str, update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        '⚠ ' + text
    )


def reply_info(text: str, update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        'ℹ️ ' + text
    )


def catch_error(log: logging.Logger):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(update: Update, context: CallbackContext):
            try:
                return func(update, context)
            except Exception as e:
                log.exception('Error: %s\nUpdate: %s', context.error, update)

                if update:
                    if isinstance(e, RetryAfter):
                        text = text_of.ERROR_RETRY_AFTER.format(int(e.retry_after))
                    elif isinstance(e, UnknownBookError):
                        text = text_of.UNKNOWN_BOOK
                    else:
                        text = text_of.ERROR

                    reply_error(text, update, context)

        return wrapper
    return actual_decorator


# SOURCE: https://github.com/gil9red/SimplePyScripts/blob/cd5bf42742b2de4706a82aecb00e20ca0f043f8e/shorten.py#L7
def shorten(text: str, length=30) -> str:
    if not text:
        return text

    if len(text) > length:
        text = text[:length] + '...'
    return text
