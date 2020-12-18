#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import re
from typing import Optional, List

# pip install bleach
import bleach

from bs4 import BeautifulSoup, Tag


PATTERN_PAGE = re.compile(r'страниц.\s*(\d+)', flags=re.IGNORECASE)
PATTERN_END = re.compile(r'конец|концу', flags=re.IGNORECASE)


def parse(obj) -> BeautifulSoup:
    return BeautifulSoup(obj, 'html.parser')


def get_text(tag: Tag, default=None) -> Optional[str]:
    if not tag:
        return default

    return tag.get_text(strip=True)


def get_href(tag: Tag) -> Optional[str]:
    if not tag or not hasattr(tag, 'attrs'):
        return None

    attrs = [v for k, v in tag.attrs.items() if ':href' in k]
    if attrs:
        return attrs[0].lstrip('#')


# SOURCE: https://github.com/gil9red/SimplePyScripts/blob/597dfd4ea77f0d57d2217ad02cde42cc23256c9b/html_parsing/random_quote_bash_im/bash_im.py#L29
def get_plaintext(element: Tag) -> str:
    items = []
    for elem in element.descendants:
        if isinstance(elem, str):
            items.append(elem.strip())
        elif elem.name in ['br', 'p']:
            items.append('\n')
    return ''.join(items).strip()


def get_section_text(
        element: Tag,
        section: str = None,
        ignored_tags=('b', 'strong', 'i', 'em', 'code', 'pre')
) -> Optional[str]:
    if not element:
        return

    html = str(element)

    html = re.sub(' {2,}', ' ', html)

    html = html\
        .replace('<p>', '').replace('</p>', '\n')\
        .replace('<br/>', '\n')

    html = bleach.clean(html, tags=ignored_tags, strip=True)

    # "на<b>синего</b>монстра!" -> "на <b>синего</b>монстра!"
    html = re.sub(r'(\w)(<\w+>)', r'\1 \2', html)

    # "на<b>синего</b>монстра!" -> "на<b>синего</b> монстра!"
    html = re.sub(r'(</\w+>)(\w)', r'\1 \2', html)

    html = re.sub(r'\n{3,}', r'\n\n', html)

    return (f'📃 Страница №{section}\n\n' if section else '') + html.strip()


def preprocess_tags(tags: List[Tag]):
    for i in reversed(range(len(tags))):
        tag = tags[i]

        # If tag is not NavigableString
        if not tag.name:
            continue

        value = get_plaintext(tag)

        if tag.name == 'emphasis':
            if PATTERN_PAGE.search(value):
                tag.replace_with(parse(f'<b>{{variant}} {value}</b>'))
            elif PATTERN_END.search(value):
                tag.replace_with(parse(f'<b>{{end}} {value}</b>'))
            else:
                tag.replace_with(parse(f'<b>{value}</b>'))

        if tag.children:
            preprocess_tags(list(tag))


def get_transitions(tags: List[Tag], func_get_page_tag=None) -> List[str]:
    transitions = []

    for x in tags:
        if func_get_page_tag:
            page_tag = func_get_page_tag(x)
        else:
            page_tag = x.emphasis

        if not page_tag:
            continue

        items = PATTERN_PAGE.findall(get_plaintext(page_tag))
        if items:
            transitions += items

    return transitions


def get_images(tags: List[Tag]) -> List[str]:
    items = []
    for x in tags:
        href = get_href(x)
        if href:
            items.append(href)
    return items


def clear_number(number_str) -> str:
    if not number_str:
        return number_str

    if isinstance(number_str, Tag):
        number_str = number_str.text

    return re.sub(r'\D', '', number_str)
