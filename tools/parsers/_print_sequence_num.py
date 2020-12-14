#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from pathlib import Path
from tools.parsers.utils import parse


for file_name in Path('Ужастики-2').glob('*.fb2'):
    root = parse(file_name.read_bytes())

    title_info_tag = root.select_one('description > title-info')

    sequence_tag = title_info_tag.select_one('sequence')
    sequence_name = sequence_tag.get('name') if sequence_tag else None
    try:
        sequence_num = sequence_tag.get('number') if sequence_tag else None
        sequence_num = int(sequence_num)
    except:
        sequence_num = None

    print('{:4}'.format(str(sequence_num)), file_name)
