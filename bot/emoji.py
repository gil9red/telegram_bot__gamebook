#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


PAGE_VARIANT = '🔷️'
PAGE_END = '❗'
VISITED_FULL = '✅'
VISITED_PARTIALLY = '✔️'

MAP = {
    '{variant}': PAGE_VARIANT,
    '{end}':     PAGE_END,
}


def replace(text: str) -> str:
    for k, v in MAP.items():
        text = text.replace(k, v)

    return text
