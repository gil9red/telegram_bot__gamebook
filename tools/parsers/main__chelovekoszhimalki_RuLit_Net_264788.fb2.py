#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from collections import defaultdict
from typing import List
from pathlib import Path

from bs4 import Tag

from config import DIR_DUMP_BOOKS
from tools.parsers.book import parse_book_info
from tools.parsers.utils import (
    parse, get_plaintext, get_section_text, get_href, preprocess_tags, get_transitions
)


# Страницы, в которых нужно монету подбрасывать
COIN_FLIP = [
    '45'
]


def is_start_section(tag: Tag) -> bool:
    if tag.name != 'p':
        return False

    value = get_plaintext(tag).lower()
    return value.isdigit()


def get_images(tags: List[Tag]) -> List[str]:
    items = []
    for x in tags:
        href = get_href(x)
        if href:
            items.append(href)
    return items


file_name = Path('Ужастики-2') / 'chelovekoszhimalki_RuLit_Net_264788.fb2'
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

for tag in root.select_one('body > section').children:
    # If tag is not NavigableString
    if not tag.name:
        continue

    if is_start_section(tag):
        section = get_plaintext(tag)

        tags = []
        section_by_tags[section] = tags
        continue

    if tags is not None:
        tags.append(tag)

end_number = 0
link_to_section = 0

for section, tags in section_by_tags.items():
    transitions = get_transitions(tags)
    images = get_images(tags)

    if not transitions:
        end_number += 1

    link_to_section += len(transitions)

    preprocess_tags(tags)
    section_tag = parse(''.join(map(str, tags)))
    html_section = get_section_text(section_tag, section)

    book.add_section(
        id=section,
        text=html_section,
        transitions=transitions,
        images=images,
        coin_flip=section in COIN_FLIP
    )

print('sections:', len(book.sections))

book.save(dir_book)
