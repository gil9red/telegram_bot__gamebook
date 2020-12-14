#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import enum
import json

from pathlib import Path
from typing import IO, List

# pip install python-telegram-bot
from telegram import InlineKeyboardButton

import networkx as nx

from bot import text as text_of
from bot.regexp import (
    fill_string_pattern, PATTERN_BOOK, PATTERN_BOOK_PAGE, PATTERN_BOOK_IMAGE, PATTERN_BOOK_ANNOTATION
)
from bot import emoji
from bot.common import join_page, pairwise, shorten


def remove_cycles(book: 'BookHelper'):
    cycles = list(nx.simple_cycles(book.G))

    # Попробуем определить какие страницы в цикле шли раньше других, чтобы
    # правильно удалить зациклинность
    for edge in cycles:
        new_edge = None
        node_1, node_2 = edge

        for paths in nx.all_simple_paths(book.G, book.first_page, node_1):
            if node_2 not in paths:
                new_edge = node_2, node_1
                break

        for paths in nx.all_simple_paths(book.G, book.first_page, node_2):
            if node_1 not in paths:
                new_edge = node_1, node_2
                break

        if new_edge:
            book.G.remove_edge(*new_edge)


class VisitedPathEnum(enum.Enum):
    NEW = enum.auto()
    PARTIALLY = enum.auto()
    FULL = enum.auto()


class BookHelper:
    def __init__(self, book_info: dict, dir_book: Path):
        self.book_info = book_info
        self.dir_book = dir_book

        self.id = self.book_info['id']
        self.title = self.book_info['title']
        self.author = self.book_info['author']
        self.annotation = self.book_info['annotation']
        self.coverpage_id = self.book_info['coverpage_id']
        self.sequence_name = self.book_info['sequence_name']
        self.sequence_num = self.book_info['sequence_num']
        self.publisher = self.book_info['publisher']
        self.sections = self.book_info['sections']

        self.first_page: str = min(list(self.sections.keys()), key=lambda x: int(x))

        self.end_pages: List[str] = [k for k, v in self.sections.items() if not v['transitions']]

        self.all_pages = set()
        for page, section in self.sections.items():
            self.all_pages.add(page)
            for to_page in section['transitions']:
                self.all_pages.add(to_page)
        self.total_pages = len(self.all_pages)

        # Graph pages
        self.G = nx.DiGraph()
        for page, section in self.sections.items():
            for to_page in section['transitions']:
                self.G.add_edge(page, to_page)

        # Пробуем удалить циклы из графа переходов, чтобы правильно отмечать
        # страницы-циклы как VisitedPathEnum.FULL после того как они будут посещены
        remove_cycles(self)

        sequence_num_text = f'#{self.sequence_num}. ' if self.sequence_num else ''
        self.title_html = '\n'.join([
            f'{sequence_num_text}<b>{self.title}</b>',
            f'Серия <b>{self.sequence_name}</b>',
            f'Автор <b>{self.author}</b>',
            '',
            f'«{shorten(self.annotation, length=200)}»',
        ])

    def get_page(self, page: str) -> str:
        path = self.dir_book / 'sections' / f'{page}.html'
        return emoji.replace(path.read_text('utf-8'))

    def get_coverpage_io(self) -> IO:
        return self.get_image_io(self.book_info['coverpage_id'])

    def get_image_io(self, image_name: str) -> IO:
        return open(self.dir_book / 'images' / image_name, 'rb')

    def get_button_book(self, text) -> InlineKeyboardButton:
        callback_data = fill_string_pattern(PATTERN_BOOK, self.id)
        return InlineKeyboardButton(text=text, callback_data=callback_data)

    def get_button_page(
            self,
            from_page: str,
            page: str,
            text: str = None,
            visited_pages: List[str] = None,
            is_visited=False
    ) -> InlineKeyboardButton:
        postfix = ''

        if visited_pages:
            result = self.check_path(page, visited_pages, is_visited)
            if result == VisitedPathEnum.FULL:
                postfix = emoji.VISITED_FULL
            elif result == VisitedPathEnum.PARTIALLY:
                postfix = emoji.VISITED_PARTIALLY

        callback_data = fill_string_pattern(PATTERN_BOOK_PAGE, self.id, from_page, page)
        return InlineKeyboardButton(text=f"{text or page} {postfix}", callback_data=callback_data)

    def get_button_first_page(self, text) -> InlineKeyboardButton:
        return self.get_button_page(self.first_page, self.first_page, text)

    def get_button_image(self, text: str, img_name: str) -> InlineKeyboardButton:
        callback_data = fill_string_pattern(PATTERN_BOOK_IMAGE, self.id, img_name)
        return InlineKeyboardButton(text=text, callback_data=callback_data)

    def get_button_annotation(self) -> InlineKeyboardButton:
        callback_data = fill_string_pattern(PATTERN_BOOK_ANNOTATION, self.id)
        return InlineKeyboardButton(text=text_of.BTN_ANNOTATION, callback_data=callback_data)

    def get_transitions(self, page: str) -> List[str]:
        return self.sections[page]['transitions']

    def get_images(self, page: str) -> List[str]:
        return self.sections[page]['images']

    def has_coin_flip(self, page: str) -> bool:
        return self.sections[page]['coin_flip']

    def check_path(self, page: str, visited_pages: List[str], is_visited: bool) -> VisitedPathEnum:
        if not is_visited:
            return VisitedPathEnum.NEW

        # Для конечной страницы пути не будут найдены в графе, поэтому нужно
        # вручную проверить, что конечная страница была посещена
        if page in self.end_pages and is_visited:
            return VisitedPathEnum.FULL

        # Сбор всех страниц от текущей, до всех возможных
        all_pages = []
        for end_page in self.end_pages:
            for paths in nx.all_simple_paths(self.G, page, end_page):
                for from_page, to_page in pairwise(paths):
                    all_pages.append(join_page(from_page, to_page))

        # Например, для страниц-циклов не будет найдено путей, т.к. ранее мы разорвали циклы
        # и страницы-циклы перестали вести куда-либо
        if not all_pages and is_visited:
            return VisitedPathEnum.FULL

        all_pages = list(set(all_pages))

        # Из общего количества страниц удаляем посещенные
        for visited_page in set(visited_pages):
            if visited_page in all_pages:
                all_pages.remove(visited_page)

        # Если пустой, значит все пути посещены
        if not all_pages:
            return VisitedPathEnum.FULL
        elif is_visited:
            return VisitedPathEnum.PARTIALLY
        else:
            return VisitedPathEnum.NEW

    @staticmethod
    def from_file(file_name: Path) -> 'BookHelper':
        book_info = json.loads(file_name.read_text('utf-8'))
        dir_book = file_name.parent

        return BookHelper(book_info, dir_book)

