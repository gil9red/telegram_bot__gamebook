#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import base64
import shutil
from pathlib import Path

from config import DIR_BOOKS, DIR_DUMP_BOOKS, FILE_NAME_BOOKS_BASE64


def pack():
    from_dir = DIR_BOOKS
    zip_name = DIR_DUMP_BOOKS / from_dir.stem

    # Make zip
    file_name_zip = shutil.make_archive(zip_name, 'zip', from_dir)
    file_name_zip = Path(file_name_zip)

    # Make base64 txt
    data = file_name_zip.read_bytes()
    data_base64 = base64.b64encode(data)
    FILE_NAME_BOOKS_BASE64.write_bytes(data_base64)

    # Remove zip
    file_name_zip.unlink()


if __name__ == '__main__':
    pack()
