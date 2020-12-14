#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import hashlib
from pathlib import Path

from tools.parsers.utils import parse


for file_name in Path('Ужастики-2').glob('*.fb2'):
    root = parse(file_name.read_bytes())

    title_info_tag = root.select_one('description > title-info')
    title = title_info_tag.select_one('book-title').text

    book_id = hashlib.sha1(title.encode('utf-8')).hexdigest()
    print(book_id)
