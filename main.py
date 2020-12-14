#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import os
import time

# pip install python-telegram-bot
from telegram.ext import Updater

from config import TOKEN
from bot.common import log
from bot import commands


def main():
    cpu_count = os.cpu_count()
    workers = cpu_count
    log.debug('System: CPU_COUNT=%s, WORKERS=%s', cpu_count, workers)

    log.debug('Start')

    updater = Updater(
        TOKEN,
        workers=workers,
        use_context=True
    )
    commands.setup(updater)

    updater.start_polling()
    updater.idle()

    log.debug('Finish')


if __name__ == '__main__':
    while True:
        try:
            main()
        except:
            log.exception('')

            timeout = 15
            log.info(f'Restarting the bot after {timeout} seconds')
            time.sleep(timeout)
