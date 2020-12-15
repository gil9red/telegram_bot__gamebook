#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from typing import Tuple

# pip install python-telegram-bot
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ReplyKeyboardMarkup, InputMediaPhoto
)
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackQueryHandler, CallbackContext

from bot.common import (
    log, log_func, reply_error, reply_info, catch_error, FILTER_BY_ADMIN, get_button_delete_message
)
from bot.cache_storage import BOOKS, get_book_id
from bot import coin_flip

from bot import text as text_of
from bot.book_helper import BookHelper
from bot.db import VisitedPage
from bot.regexp import (
    fill_string_pattern, PATTERN_BOOK, PATTERN_BOOK_PAGE, PATTERN_BOOK_IMAGE, PATTERN_BOOK_ANNOTATION,
    PATTERN_SELECT_BOOKS, PATTERN_DELETE_MESSAGE, PATTERN_GET_PAGE, PATTERN_ON_HELP, PATTERN_ON_CLEAR
)


def reply_help(update: Update, context: CallbackContext):
    reply_markup = ReplyKeyboardMarkup.from_button(
        text_of.BTN_TO_SELECT_BOOKS, resize_keyboard=True
    )

    update.effective_message.reply_html(
        text_of.WELCOME,
        reply_markup=reply_markup,
    )


@catch_error(log)
@log_func(log)
def on_start(update: Update, context: CallbackContext):
    reply_help(update, context)


@catch_error(log)
@log_func(log)
def on_help(update: Update, context: CallbackContext):
    reply_help(update, context)


@catch_error(log)
@log_func(log)
def on_clear(update: Update, context: CallbackContext):
    num = VisitedPage.delete().execute()
    reply_info(f"Удалено {num} записей", update, context)


def reply_select_books(update: Update, context: CallbackContext):
    query = update.callback_query
    message = update.effective_message

    # Если функция вызвана из CallbackQueryHandler
    if query:
        query.answer()
        current_index = int(context.match.group(1))
    else:
        current_index = 0

    prev_index = (current_index - 1) % len(BOOKS)
    next_index = (current_index + 1) % len(BOOKS)

    book = BOOKS[current_index]

    cover = book.get_coverpage_io()
    title = book.title_html

    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text_of.BTN_PREV, callback_data=fill_string_pattern(PATTERN_SELECT_BOOKS, prev_index)),
            InlineKeyboardButton(text_of.BTN_NEXT, callback_data=fill_string_pattern(PATTERN_SELECT_BOOKS, next_index))
        ],
        [book.get_button_book(text_of.BTN_SELECT_BOOK)]
    ])

    if query:
        message.edit_media(
            InputMediaPhoto(cover, title, parse_mode=ParseMode.HTML),
            reply_markup=reply_markup
        )
    else:
        message.reply_photo(
            cover, title, reply_markup=reply_markup, parse_mode=ParseMode.HTML
        )


@catch_error(log)
@log_func(log)
def on_select_books(update: Update, context: CallbackContext):
    reply_select_books(update, context)


@catch_error(log)
@log_func(log)
def on_callback_select_books(update: Update, context: CallbackContext):
    reply_select_books(update, context)


@catch_error(log)
@log_func(log)
def on_callback_book(update: Update, context: CallbackContext):
    message = update.effective_message

    query = update.callback_query
    query.answer()

    _, book = get_book_id(context)

    button_row1 = []
    if book.coverpage_id:
        button_row1.append(
            book.get_button_image(text_of.BTN_COVER, book.coverpage_id)
        )

    if book.annotation:
        button_row1.append(
            book.get_button_annotation()
        )

    buttons = []
    if button_row1:
        buttons.append(button_row1)
    buttons.append([book.get_button_first_page(text=text_of.BTN_START)])

    reply_markup = InlineKeyboardMarkup(buttons)

    text = book.title_html

    is_new = message.text is None
    if is_new:
        message.reply_html(
            text,
            reply_markup=reply_markup
        )
    else:
        message.edit_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
        )


@catch_error(log)
@log_func(log)
def on_callback_annotation(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    _, book = get_book_id(context)
    reply_markup = InlineKeyboardMarkup.from_button(
        book.get_button_book(text_of.BTN_BACK)
    )

    query.message.edit_text(
        book.annotation,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
    )


def get_book_page(book: BookHelper, page: str, update: Update) -> Tuple[str, InlineKeyboardMarkup]:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    book_id = book.id
    to_pages = book.get_transitions(page)

    buttons = []
    if to_pages:
        button_row1 = []
        for next_page in to_pages:
            is_visited = VisitedPage.has(chat_id, user_id, book_id, page, next_page)
            visited_pages = VisitedPage.get_all_pages(chat_id, user_id, book_id)

            button_row1.append(
                book.get_button_page(
                    from_page=page, page=next_page,
                    visited_pages=visited_pages, is_visited=is_visited
                )
            )
        buttons.append(button_row1)

        if book.has_coin_flip(page):
            buttons.append(
                [coin_flip.get_button_coin_flip(text_of.BTN_COIN_FLIP)]
            )

    else:
        buttons.append([
            book.get_button_first_page(text=text_of.BTN_RENEW),
            book.get_button_book(text_of.BTN_RETURN_TO_BOOK)
        ])

    images = book.get_images(page)
    if images:
        buttons.append([
            book.get_button_image(text_of.BTN_IMAGE.format(i), img)
            for i, img in enumerate(images, 1)
        ])

    reply_markup = InlineKeyboardMarkup(buttons)
    text = book.get_page(page)
    return text, reply_markup


@catch_error(log)
@log_func(log)
def on_callback_page(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    book_id, book = get_book_id(context)
    from_page = context.match.group(2)
    page = context.match.group(3)

    # Отмечать страницу как посещенный можно только в этом методе
    VisitedPage.add(chat_id, user_id, book_id, from_page, page)
    text, reply_markup = get_book_page(book, page, update)

    query.message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
    )


@catch_error(log)
@log_func(log)
def on_get_page(update: Update, context: CallbackContext):
    _, book = get_book_id(context)
    page = context.match.group(2)

    # В этой команде нельзя узнать from_page, поэтому просто дублируем текущее
    # Просто, в этой странице не будет отмечены
    text, reply_markup = get_book_page(book, page, update)

    update.effective_message.reply_html(
        text,
        reply_markup=reply_markup,
    )


@catch_error(log)
@log_func(log)
def on_callback_image(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    book_id, book = get_book_id(context)
    image_name = context.match.group(2)

    reply_markup = InlineKeyboardMarkup.from_button(
        get_button_delete_message(text_of.BTN_HIDE_IMAGE)
    )

    query.message.reply_photo(
        photo=book.get_image_io(image_name),
        reply_markup=reply_markup,
        reply_to_message_id=query.message.message_id
    )


@catch_error(log)
@log_func(log)
def on_callback_delete_message(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    query.message.delete()


@catch_error(log)
def on_error(update: Update, context: CallbackContext):
    log.exception('Error: %s\nUpdate: %s', context.error, update)
    if update:
        reply_error(text_of.ERROR, update, context)


def setup(updater: Updater):
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', on_start, run_async=True))
    dp.add_handler(MessageHandler(Filters.regex(PATTERN_ON_HELP), on_help, run_async=True))

    # Команда админа: получение конкретной страницы в книге
    dp.add_handler(MessageHandler(FILTER_BY_ADMIN & Filters.regex(PATTERN_GET_PAGE), on_get_page, run_async=True))

    # Команда админа: очищение базы данных
    dp.add_handler(CommandHandler('clear', on_clear, FILTER_BY_ADMIN, run_async=True))
    dp.add_handler(MessageHandler(FILTER_BY_ADMIN & Filters.regex(PATTERN_ON_CLEAR), on_clear, run_async=True))

    dp.add_handler(MessageHandler(Filters.text, on_select_books, run_async=True))
    dp.add_handler(CallbackQueryHandler(on_callback_select_books, pattern=PATTERN_SELECT_BOOKS, run_async=True))

    dp.add_handler(CallbackQueryHandler(on_callback_book, pattern=PATTERN_BOOK, run_async=True))
    dp.add_handler(CallbackQueryHandler(on_callback_page, pattern=PATTERN_BOOK_PAGE, run_async=True))
    dp.add_handler(CallbackQueryHandler(on_callback_annotation, pattern=PATTERN_BOOK_ANNOTATION, run_async=True))
    dp.add_handler(CallbackQueryHandler(on_callback_image, pattern=PATTERN_BOOK_IMAGE, run_async=True))
    dp.add_handler(CallbackQueryHandler(on_callback_delete_message, pattern=PATTERN_DELETE_MESSAGE, run_async=True))

    coin_flip.setup(updater)

    dp.add_error_handler(on_error, run_async=True)
