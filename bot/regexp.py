#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import re


PATTERN_BOOK = re.compile(r'^book_([a-fA-F\d]+)$')
PATTERN_BOOK_PAGE = re.compile(r'^([a-fA-F\d]+)_page_from_(\d+)_to_(\d+)$')
PATTERN_BOOK_IMAGE = re.compile(r'^([a-fA-F\d]+)_image_(.+)$')
PATTERN_BOOK_ANNOTATION = re.compile(r'^([a-fA-F\d]+)_annotation$')
PATTERN_SELECT_BOOKS = re.compile(r'^show_book_(\d+)$')
PATTERN_GET_PAGE = re.compile(r'^([a-fA-F\d]+) (\d+)$')
PATTERN_DELETE_MESSAGE = re.compile('^delete_message$')
PATTERN_ON_CLEAR = re.compile('(?i)^clear$')


def fill_string_pattern(pattern: re.Pattern, *args) -> str:
    pattern = pattern.pattern
    pattern = pattern.strip('^$')
    return re.sub(r'\(.+?\)', '{}', pattern).format(*args)
