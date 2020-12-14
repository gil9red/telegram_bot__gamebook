#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import base64
import shutil
from urllib.parse import urljoin
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from config import DIR_BOOKS, DIR_DUMP_BOOKS


URL = 'https://gist.github.com/gil9red/b404932c6118a92bba9180d2f20fe801'

session = requests.session()
session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0'


def download() -> Path:
    rs = session.get(URL)
    root = BeautifulSoup(rs.content, 'html.parser')

    a = root.find('a', attrs={'role': 'button'}, text='Raw')
    if not a:
        raise Exception('Not found "Raw" in gists!')

    url_file = urljoin(rs.url, a['href'])
    data_base64 = session.get(url_file).content

    data = base64.b64decode(data_base64)

    file_name_zip = DIR_DUMP_BOOKS / 'books.zip'
    file_name_zip.write_bytes(data)

    return file_name_zip


def unpack():
    if DIR_BOOKS.exists():
        print('DIR_BOOKS already exists! Skip!')
        return

    file_name_zip = download()

    shutil.unpack_archive(file_name_zip, DIR_BOOKS)

    file_name_zip.unlink()


if __name__ == '__main__':
    unpack()
