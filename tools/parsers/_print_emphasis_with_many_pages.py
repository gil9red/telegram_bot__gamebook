#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from pathlib import Path
from tools.parsers.utils import parse, PATTERN_PAGE


for file_name in Path('Ужастики-2').glob('*.fb2'):
    root = parse(file_name.read_bytes())

    for x in root.select('emphasis'):
        if len(PATTERN_PAGE.findall(x.text)) > 1:
            print(f'{x.text!r}!!!', file_name)
