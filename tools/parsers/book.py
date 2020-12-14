#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import base64
import json
import hashlib
from dataclasses import dataclass, field, asdict
from typing import List, Dict
from pathlib import Path

from bs4 import Tag

from config import COVER_HEIGHT
from tools.parsers.utils import get_text, get_section_text, get_href

# pip install pillow
from PIL import Image


FILE_NAME_BOOK = 'book.json'
FILE_NAME_DIR_SECTIONS = 'sections'
FILE_NAME_DIR_IMAGES = 'images'


@dataclass
class Section:
    id: str
    text: str
    transitions: List[int] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    coin_flip: bool = False


@dataclass
class Book:
    id: str
    title: str
    author: str
    annotation: str = None
    coverpage_id: str = None
    sequence_name: str = None
    sequence_num: int = None
    publisher: str = None
    sections: List[Section] = field(default_factory=list)
    images: Dict[str, bytes] = field(default_factory=dict)

    def add_section(
            self,
            id: str,
            text: str,
            transitions: List[int] = None,
            images: List[str] = None,
            coin_flip: bool = False
    ):
        page = Section(id, text, coin_flip=coin_flip)

        if transitions is not None:
            page.transitions = transitions

        if images is not None:
            page.images = images

        self.sections.append(page)

    def save(self, dir_book: Path):
        dir_book.mkdir(parents=True, exist_ok=True)

        dir_book_sections = dir_book / FILE_NAME_DIR_SECTIONS
        dir_book_sections.mkdir(parents=True, exist_ok=True)

        dir_book_images = dir_book / FILE_NAME_DIR_IMAGES
        dir_book_images.mkdir(parents=True, exist_ok=True)

        book_info = asdict(self)

        book_info['sections'] = dict()
        for section in self.sections:
            section_data = asdict(section)
            section_data.pop('text')  # Текст будет храниться в файлах

            section_id = section_data['id']
            book_info['sections'][section_id] = section_data

            section_data.pop('id')  # Id будет известен в ключе

            path_section = dir_book_sections / f'{section.id}.html'
            path_section.write_text(section.text, 'utf-8')

        # В отличии от Book, в json будет список
        book_info['images'] = []
        for file_name, img_data in self.images.items():
            book_info['images'].append(file_name)

            path_img = dir_book_images / file_name
            path_img.write_bytes(img_data)

        # Для единобразия обложек установим им одинаковую высоту
        file_name_cover = dir_book_images / self.coverpage_id

        img = Image.open(file_name_cover)
        hpercent = COVER_HEIGHT / float(img.size[1])
        wsize = int(img.size[0] * hpercent)
        img = img.resize((wsize, COVER_HEIGHT), Image.ANTIALIAS)
        img.save(file_name_cover)

        json.dump(
            book_info,
            open(dir_book / FILE_NAME_BOOK, 'w', encoding='utf-8'),
            ensure_ascii=False,
            indent=4
        )


def parse_book_info(root: Tag) -> Book:
    title_info_tag = root.select_one('description > title-info')

    title = get_text(title_info_tag.select_one('book-title'))
    book_id = hashlib.sha1(title.encode('utf-8')).hexdigest()

    author_first_name = get_text(title_info_tag.select_one('author > first-name'), "")
    author_middle_name = get_text(title_info_tag.select_one('author > middle-name'), "")
    author_last_name = get_text(title_info_tag.select_one('author > last-name'), "")
    author = ' '.join(filter(None, [author_first_name, author_middle_name, author_last_name]))

    annotation = get_section_text(title_info_tag.select_one('annotation'))

    coverpage_tag = title_info_tag.select_one('coverpage > image')
    coverpage_id = get_href(coverpage_tag)

    sequence_tag = title_info_tag.select_one('sequence')
    sequence_name = sequence_tag.get('name') if sequence_tag else None
    try:
        sequence_num = sequence_tag.get('number') if sequence_tag else None
        sequence_num = int(sequence_num)
    except:
        sequence_num = None

    publisher = get_text(root.select_one('publish-info > publisher'))

    images = dict()
    for binary in root.select('binary'):
        if 'image/' not in binary['content-type']:
            continue

        file_name = binary['id']
        img_data = binary.get_text(strip=True)
        img_data = base64.b64decode(img_data)

        images[file_name] = img_data

    return Book(
        id=book_id,
        title=title,
        author=author,
        annotation=annotation,
        coverpage_id=coverpage_id,
        sequence_name=sequence_name,
        sequence_num=sequence_num,
        publisher=publisher,
        images=images,
    )
