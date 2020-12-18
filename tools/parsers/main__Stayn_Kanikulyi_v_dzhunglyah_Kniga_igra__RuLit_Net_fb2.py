#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from tools.parsers.utils import DIR
from tools.parsers.main__noch_v_lesu_oborotnej_RuLiter_Ru_12541_fb2 import parse_fb2


file_name = DIR / 'Ужастики-2' / 'Stayn_Kanikulyi_v_dzhunglyah_Kniga-igra__RuLit_Net.fb2'

# Страницы, в которых нужно монету подбрасывать
COIN_FLIP = [
    '48'
]

if __name__ == '__main__':
    parse_fb2(file_name, coin_flip=COIN_FLIP)
