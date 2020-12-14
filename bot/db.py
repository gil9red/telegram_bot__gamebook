#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import datetime as DT
from typing import List

# pip install peewee
from peewee import (
    Model, TextField, ForeignKeyField, DateTimeField, IntegerField
)
from playhouse.sqliteq import SqliteQueueDatabase

from config import DB_DIR_NAME, DB_FILE_NAME
from bot.common import shorten, join_page


DB_DIR_NAME.mkdir(parents=True, exist_ok=True)


# This working with multithreading
# SOURCE: http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#sqliteq
db = SqliteQueueDatabase(
    DB_FILE_NAME,
    pragmas={
        'foreign_keys': 1,
        'journal_mode': 'wal',    # WAL-mode
        'cache_size': -1024 * 64  # 64MB page-cache
    },
    use_gevent=False,    # Use the standard library "threading" module.
    autostart=True,
    queue_max_size=64,   # Max. # of pending writes that can accumulate.
    results_timeout=5.0  # Max. time to wait for query to be executed.
)


class BaseModel(Model):
    class Meta:
        database = db

    def __str__(self):
        fields = []
        for k, field in self._meta.fields.items():
            v = getattr(self, k)

            if isinstance(field, TextField):
                if v:
                    v = repr(shorten(v))

            elif isinstance(field, ForeignKeyField):
                k = f'{k}_id'
                if v:
                    v = v.id

            fields.append(f'{k}={v}')

        return self.__class__.__name__ + '(' + ', '.join(fields) + ')'


class VisitedPage(BaseModel):
    user_id = IntegerField()
    chat_id = IntegerField()
    book_id = TextField()
    page = TextField()
    datetime = DateTimeField(default=DT.datetime.now)

    @classmethod
    def has(cls, user_id: int, chat_id: int, book_id: str, from_page: str, page: str) -> bool:
        page = join_page(from_page, page)

        return bool(cls.get_or_none(
            cls.user_id == user_id,
            cls.chat_id == chat_id,
            cls.book_id == book_id,
            cls.page == page,
        ))

    @classmethod
    def get_all_pages(cls, user_id: int, chat_id: int, book_id: str) -> List[str]:
        query = (
            cls
            .select(cls.page)
            .distinct()
            .where(
                cls.user_id == user_id,
                cls.chat_id == chat_id,
                cls.book_id == book_id
            )
        )
        return [x.page for x in query]

    @classmethod
    def add(cls, user_id: int, chat_id: int, book_id: str, from_page: str, page: str) -> 'VisitedPage':
        page = join_page(from_page, page)

        return cls.create(
            user_id=user_id,
            chat_id=chat_id,
            book_id=book_id,
            page=page,
        )


db.connect()
db.create_tables([VisitedPage])


if __name__ == '__main__':
    test_user_id = -1
    test_chat_id = -1
    test_book_id = '123'
    test_page = '999'

    ok = VisitedPage.has(
        test_user_id, test_chat_id, test_book_id, test_page
    )
    print(ok)
    assert ok is False

    visited_page = VisitedPage.add(
        test_user_id, test_chat_id, test_book_id, test_page
    )

    ok = VisitedPage.has(
        test_user_id, test_chat_id, test_book_id, test_page
    )
    print(ok)
    assert ok is True

    visited_page.delete_instance()
