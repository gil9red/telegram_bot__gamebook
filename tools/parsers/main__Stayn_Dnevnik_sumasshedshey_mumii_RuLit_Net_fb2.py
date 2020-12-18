#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from tools.parsers.main__noch_v_lesu_oborotnej_RuLiter_Ru_12541_fb2 import parse_fb2
from tools.parsers.utils import get_transitions, DIR


file_name = DIR / 'Ужастики-2' / 'Stayn_Dnevnik_sumasshedshey_mumii_RuLit_Net.fb2'

# Страницы, в которых нужно монету подбрасывать
COIN_FLIP = [
    '15', '35', '69'
]


if __name__ == '__main__':
    parse_fb2(
        file_name,
        lambda tags: get_transitions(tags, lambda tag: tag.p),
        COIN_FLIP
    )
