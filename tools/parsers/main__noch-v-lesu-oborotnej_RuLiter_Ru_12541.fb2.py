#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from collections import defaultdict
from pathlib import Path

from bs4 import Tag

from config import DIR_DUMP_BOOKS
from tools.parsers.book import parse_book_info
from tools.parsers.utils import (
    parse, get_section_text, preprocess_tags, get_transitions, clear_number, get_images, get_plaintext
)


def is_start_section(tag: Tag) -> bool:
    if tag.name != 'p':
        return False

    value = get_plaintext(tag).lower()
    return value.isdigit()


file_name = Path('Ужастики-2') / 'noch-v-lesu-oborotnej_RuLiter_Ru_12541.fb2'
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

dir_book = DIR_DUMP_BOOKS / file_name

section_by_tags = defaultdict(list)
tags = None

for section in root.select('body > section'):
    section_id = clear_number(section.select_one('title > p'))
    if not section_id:
        section_id = "0"

    # Удаление тегов-заголовков с номерами страниц
    for title in section.select('title'):
        title.decompose()

    tags = section.find_all(recursive=False)

    transitions = get_transitions(tags, lambda tag: tag.p and tag.p.emphasis)
    images = get_images(tags)

    preprocess_tags(tags)
    section_tag = parse(''.join(map(str, tags)))
    html_section = get_section_text(section_tag, None if section_id == '0' else section_id)

    book.add_section(
        id=section_id,
        text=html_section,
        transitions=transitions,
        images=images,
    )

print('sections:', len(book.sections))

book.save(dir_book)
