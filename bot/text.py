#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from bot import emoji


ERROR = 'Возникла какая-то проблема. Попробуйте повторить запрос или попробовать чуть позже...'
ERROR_RETRY_AFTER = 'Слишком много запросов отправлено! Придется подождать {} секунд'
UNKNOWN_BOOK = 'Ой-ой что-то с книгой произошло плохое, попробуйте выбрать ее снова или другую'

SELECT_BOOKS = "Выбор книг:"

BTN_START = '📖 Начать'
BTN_RENEW = '🔄 Заново'
BTN_COVER = '📕 Обложка'
BTN_BACK = '⬅️ Назад'
BTN_ANNOTATION = '📜 Аннотация'
BTN_SHOW_IMAGE = '🖼️ Посмотреть картинку'
BTN_HIDE_IMAGE = '❌ Спрятать картинку'
BTN_TO_SELECT_BOOKS = "📖 К списку книг!"
BTN_RETURN_TO_BOOK = "📖 Вернуться к книге"
BTN_IMAGE = '🖼️ Картинка #{}'
BTN_PREV = '⬅️'
BTN_NEXT = '➡️'
BTN_SELECT_BOOK = '📖 Выбрать'

BTN_COIN_FLIP = '🍀 Бросить монету'
BTN_COIN_FLIP_RESULT = '🍀 Бросок'
BTN_COIN_FLIP_REPEAT = '🔁 Повторить'
BTN_COIN_FLIP_HIDE = '❌ Убрать'

WELCOME = f'''
Начните взаимодействие с клика на кнопку {BTN_TO_SELECT_BOOKS!r}.

Для удобства работы на кнопки переходов добавляются эмодзи:
    {emoji.VISITED_FULL} — все страницы уже были просмотрены
    {emoji.VISITED_PARTIALLY} — не все страницы были просмотрены
'''.strip()
