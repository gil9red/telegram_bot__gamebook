#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import os
from pathlib import Path


DIR = Path(__file__).resolve().parent
DIR_BOOKS = DIR / 'books'
DIR_DUMP_BOOKS = DIR / 'dump_books'
FILE_NAME_BOOKS_BASE64 = DIR_DUMP_BOOKS / 'books_base64.txt'

DIR_LOG = DIR / 'logs'

DB_DIR_NAME = DIR / 'database'
DB_FILE_NAME = str(DB_DIR_NAME / 'database.sqlite')

TOKEN_FILE_NAME = DIR / 'TOKEN.txt'
TOKEN = os.environ.get('TOKEN') or TOKEN_FILE_NAME.read_text('utf-8').strip()

ADMIN_USERNAME = '@ilya_petrash'

COVER_HEIGHT = 300
