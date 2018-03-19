from sqlalchemy import (
    create_engine, Column, BigInteger, MetaData, Table, String)
from sqlalchemy.sql import select

from . import config


metadata = MetaData()


# Table Definitions

asana_sync_tokens = Table(
    'asana_sync_tokens', metadata,
    Column('project_id', BigInteger, index=True, primary_key=True),
    Column('sync_token', String, nullable=False))


# Functions

def init_db_engine(echo=False):
    engine = create_engine(config.DB_ENGINE_URL, echo=echo)
    metadata.create_all(engine)
    return engine


def get_existing_sync_tokens(db_engine, project_ids):
    if not project_ids:
        return {}

    conn = db_engine.connect()
    sync_tokens = dict(conn.execute(select([asana_sync_tokens]).where(
        asana_sync_tokens.c.project_id.in_(project_ids))
    ).fetchall())

    return sync_tokens


def save_sync_token(db_engine, project_id, sync_token):
    conn = db_engine.connect()
    with conn.begin():
        conn.execute(asana_sync_tokens.delete().where(
            asana_sync_tokens.c.project_id == project_id))
        conn.execute(
            asana_sync_tokens.insert(), project_id=project_id,
            sync_token=sync_token)
