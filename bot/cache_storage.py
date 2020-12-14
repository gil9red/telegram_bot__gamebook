#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from typing import Tuple

from telegram.ext import CallbackContext

from bot.book_helper import BookHelper
from bot.common import log
from bot.exceptions import UnknownBookError

from config import DIR_BOOKS
from tools.books_unpack import unpack as prepare_books


prepare_books()


ID_BY_BOOK = dict()

for file_name in DIR_BOOKS.rglob('book.json'):
    book = BookHelper.from_file(file_name)
    if book.id in ID_BY_BOOK:
        log.warn(f'Found duplicate book, title: "{book.title!r}"')
        continue

    ID_BY_BOOK[book.id] = book

# Если номер серии не задан, то пусть книга будет в конце списка
BOOKS = list(sorted(ID_BY_BOOK.values(), key=lambda x: x.sequence_num or 9999))

log.debug(f'Total books: {len(BOOKS)}')


def get_book_id(context: CallbackContext) -> Tuple[str, BookHelper]:
    book_id = context.match.group(1)
    if book_id not in ID_BY_BOOK:
        raise UnknownBookError(book_id)

    return book_id, ID_BY_BOOK[book_id]
