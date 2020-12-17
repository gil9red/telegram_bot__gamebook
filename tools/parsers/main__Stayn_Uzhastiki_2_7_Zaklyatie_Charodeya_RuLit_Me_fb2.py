#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from pathlib import Path
from tools.parsers.main__noch_v_lesu_oborotnej_RuLiter_Ru_12541_fb2 import parse_fb2


DIR = Path(__file__).resolve().parent
file_name = DIR / 'Ужастики-2' / 'Stayn_Uzhastiki-2_7_Zaklyatie-Charodeya_RuLit_Me.fb2'


if __name__ == '__main__':
    parse_fb2(file_name)
