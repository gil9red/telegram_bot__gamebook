#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from pathlib import Path
from tools.parsers.main__chelovekoszhimalki_RuLit_Net_264788_fb2 import parse_fb2


DIR = Path(__file__).resolve().parent

# Страницы, в которых нужно монету подбрасывать
COIN_FLIP = [
    '89'
]


if __name__ == '__main__':
    file_name = DIR / 'Ужастики-2' / 'Stajn_Robert_-_Cirk-Zapadnya.fb2'
    parse_fb2(file_name, COIN_FLIP)
