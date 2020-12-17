#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import subprocess
import sys

from pathlib import Path


DIR = Path(__file__).resolve().parent
DIR_PARSERS = DIR / 'parsers'


for file_name in DIR_PARSERS.glob('main__*fb2.py'):
    file_name = str(file_name)
    print('[RUN]:', file_name)

    subprocess.run([sys.executable, file_name])

    print('\n' + '-' * 100 + '\n')
