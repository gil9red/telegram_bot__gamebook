#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from collections import defaultdict

from config import DIR_DUMP_BOOKS
from tools.parsers.book import parse_book_info
from tools.parsers.utils import (
    parse, get_section_text, preprocess_tags, get_transitions, clear_number, get_images, DIR
)


# Страницы, в которых нужно монету подбрасывать
COIN_FLIP = [
    '52'
]


file_name = DIR / 'Ужастики-2' / 'Stayn_Beregis-Lilovoy-Pasty-_RuLit_Me.fb2'
print(file_name)

root = parse(file_name.read_bytes())
book = parse_book_info(root)

# print('book:', book)
print('title:', book.title)
print('author:', book.author)
print('annotation:', repr(book.annotation))
print('coverpage_id:', book.coverpage_id)
print('sequence_name:', book.sequence_name)
print('sequence_num:', book.sequence_num)
print('publisher:', book.publisher)
print('images:', list(book.images))

dir_book = DIR_DUMP_BOOKS / file_name.name

section_by_tags = defaultdict(list)

i = 0
for section_el in root.select('body > section[id]'):
    i += 1
    # print(f'{i:4}.')

    # Удаление тегов вида: <a l:href="#n_23" type="note">*</a>
    for note_tag in section_el.select('a[type="note"]'):
        note_tag.decompose()

    # Удаление тегов-заголовков с номерами страниц
    for title in section_el.select('title'):
        title.decompose()

    section = clear_number(section_el['id'])
    tags = section_el.find_all(recursive=False)

    transitions = get_transitions(tags)
    images = get_images(tags)

    preprocess_tags(tags)
    section_tag = parse(''.join(map(str, tags)))
    html_section = get_section_text(section_tag, None if section == '0' else section)

    book.add_section(
        id=section,
        text=html_section,
        transitions=transitions,
        images=images,
        coin_flip=section in COIN_FLIP
    )

    # print('\n' + '-' * 100 + '\n')

print('sections:', len(book.sections))

book.save(dir_book)
