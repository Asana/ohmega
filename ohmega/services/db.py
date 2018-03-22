from __future__ import print_function

import json

from six import add_metaclass
from sqlalchemy import (
    create_engine, Column, BigInteger, MetaData, Table, String)
from sqlalchemy.sql import select


DB_ENGINE_URL = 'sqlite:///ohmega.db'


metadata = MetaData()


# Table Definitions

asana_sync_tokens = Table(
    'asana_sync_tokens', metadata,
    Column('resource_id', BigInteger, index=True, primary_key=True),
    Column('sync_token', String, nullable=False))

asana_oauth_tokens = Table(
    'asana_oauth_tokens', metadata,
    Column('oauth_token', String, index=True, primary_key=True))


# TODO: Move somewhere else, if necessary.
class Singleton(type):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super(Singleton, cls).__call__(
                *args, **kwargs)
        return cls.__instances[cls]


@add_metaclass(Singleton)
class DBManager(object):

    def __init__(self, echo=False):
        self._db_engine = None
        self._echo = echo

    @property
    def db_engine(self):
        if not self._db_engine:
            self._db_engine = create_engine(DB_ENGINE_URL, echo=self._echo)
            metadata.create_all(self._db_engine)
        return self._db_engine


# Event Tokens

def get_sync_tokens(resource_ids):
    if not resource_ids:
        return {}

    conn = DBManager().db_engine.connect()
    sync_tokens = conn.execute(
        select([
            asana_sync_tokens.c.resource_id,
            asana_sync_tokens.c.sync_token]
        ).where(asana_sync_tokens.c.resource_id.in_(resource_ids))).fetchall()

    return dict(sync_tokens)


def save_sync_token(resource_id, sync_token):
    conn = DBManager().db_engine.connect()
    with conn.begin():
        conn.execute(asana_sync_tokens.delete().where(
            asana_sync_tokens.c.resource_id == resource_id))
        conn.execute(
            asana_sync_tokens.insert(), resource_id=resource_id,
            sync_token=sync_token)


# OAuth Tokens

def get_oauth_token():
    oauth_token = None
    conn = DBManager().db_engine.connect()

    oauth_token_row = conn.execute(
        select([asana_oauth_tokens.c.oauth_token])).first()
    if oauth_token_row:
        oauth_token = json.loads(
            oauth_token_row[asana_oauth_tokens.c.oauth_token])
    else:
        oauth_token = None

    return oauth_token


def save_oauth_token(token):
    conn = DBManager().db_engine.connect()

    with conn.begin():
        conn.execute(asana_oauth_tokens.delete())
        conn.execute(
            asana_oauth_tokens.insert(), oauth_token=json.dumps(token))

    return token
