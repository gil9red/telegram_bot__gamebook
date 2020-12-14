#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import base64
from pathlib import Path
from io import BytesIO

from tools.parsers import parse

from PIL import Image


COVER_HEIGHT = 400

path = Path('_extract_images.py_dumps')
path.mkdir(parents=True, exist_ok=True)

for file_name in Path('Ужастики-2').glob('*.fb2'):
    root = parse(file_name.read_bytes())

    images = dict()
    for binary in root.select('binary'):
        if 'image/' not in binary['content-type']:
            continue

        img_file_name = binary['id']
        if not img_file_name.startswith('cover.'):
            continue

        img_data = binary.get_text(strip=True)
        img_data = base64.b64decode(img_data)

        img = Image.open(BytesIO(img_data))
        print(img.size, file_name.stem, img_file_name)

        img_file_name = path / (file_name.stem + '.jpg')
        img_file_name.write_bytes(img_data)

        img_file_name_short = path / (file_name.stem + '_short.jpg')

        hpercent = COVER_HEIGHT / float(img.size[1])
        wsize = int(img.size[0] * hpercent)
        img = img.resize((wsize, COVER_HEIGHT), Image.ANTIALIAS)
        img.save(img_file_name_short, "JPEG")
