# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import uuid
import weakref
import hashlib
import logging


import vulkn.engines
from vulkn.utils import timer, LogLevels


timing = False
enable_parser = True


log = logging.getLogger()
logging.addLevelName(LogLevels.SQL, 'SQL')


class CacheMode:
    Table=1
    Normal=2
    Array=3
    Merge=4


class TTL:
    Session=1
    

class ClickHouseEnvironment:
    def __init__(self, ctx):
        self._ctx = ctx

    @property
    def settings(self):
        sql = 'SELECT name, value, changed FROM system.settings ORDER BY changed = 1 DESC, name'
        return self._ctx.q(sql).exec()


class VulknSession:
    def __init__(self, ctx, cache_location='vulkn'):
        self._ctx = ctx
        self._cache_location = cache_location
        self._uuid = uuid.uuid4().hex
        self._cache = []
        self._needs_optimize = True
        self.createSession()
        self._finalizer = weakref.finalize(self, self._destroyCache, ctx, self._cache)

    def optimize(self, final=False):
        if self._needs_optimize:
            self._ctx._conn.execute(
                'OPTIMIZE TABLE {session_store} {final}'.format(session_store=self.session_store,
                                                                final='FINAL' if final else ''))
            if final:
                self._needs_optimize = False

    @property
    def session_store(self):
        return '{cache_location}.session_{uuid}'.format(cache_location=self._cache_location,
                                                        uuid=self._uuid)

    def createSession(self):
        cache_ref = self.session_store
        cache_location = self._cache_location
        ctx = self._ctx
        cache_source_sql = f"""
            CREATE TABLE {cache_ref} (
                t_ts DateTime CODEC(LZ4)
            ) ENGINE = MergeTree()
            ORDER BY tuple()"""
        ctx.exec(f'CREATE DATABASE IF NOT EXISTS {cache_location}')
        ctx.exec(f'DROP TABLE IF EXISTS {cache_ref}')
        ctx.exec(cache_source_sql)
        ctx.exec(f'INSERT INTO {cache_ref} VALUES (now())')
        self._cache.append(VulknCachedObject(cache_ref, cache_source_sql))

    def destroySession(self):
        self._finalizer()

    @staticmethod
    def _destroyCache(ctx, cache):
        log.info('Purging cache...')
        for c in cache:
            if isinstance(c, VulknCachedObject):
                if c.ttl == TTL.Session and c.mode == CacheMode.Table:
                    ctx._conn.execute('DROP TABLE IF EXISTS {}'.format(c.ref))
            else:
                ctx._conn.execute('DROP TABLE IF EXISTS {}'.format(c))

    def _create_table_cache(self, obj_hash, obj_query, engine):
        ctx = self._ctx
        cache_location = self._cache_location
        cache_tmp = 'session_{uuid}_v_{obj_hash}'.format(uuid=self._uuid, obj_hash=obj_hash)
        ctx._conn.execute(f'DROP TABLE IF EXISTS {cache_location}.{cache_tmp}')
        ctx._conn.execute(f'CREATE TABLE {cache_location}.{cache_tmp} ENGINE = {engine} AS {obj_query}')
        return VulknCachedObject(f'{cache_location}.{cache_tmp}', obj_query)

    def _store_array_vector(self, obj_hash, obj_query):
        ctx = self._ctx
        cache_location = self._cache_location
        cache_tmp = 'session_{uuid}_v_{obj_hash}'.format(uuid=self._uuid, obj_hash=obj_hash)
        ctx._conn.execute(f'DROP TABLE IF EXISTS {cache_location}.{cache_tmp}')
        ctx._conn.execute(f"""
            CREATE TABLE {cache_location}.{cache_tmp}
                ENGINE = Join(ANY, LEFT, r)
            AS 
            SELECT
                1 AS r
                , v
            FROM ({obj_query})""")
        return VulknCachedObject(f'{cache_location}.{cache_tmp}', obj_query)

    def _store_object(self, obj_hash, obj_query, optimize):
        session_store = self.session_store
        session_column_name = 'var_{}'.format(obj_hash)
        self._ctx._conn.execute(f"""
            ALTER TABLE {session_store} 
                ADD COLUMN IF NOT EXISTS {session_column_name}
                    MATERIALIZED {obj_query} CODEC(LZ4)""")
        self._needs_optimize = True
        if optimize:
            self.optimize(final=True)
        return VulknCachedObject(session_column_name, obj_query, mode=CacheMode.Normal)

    def cache(self, obj, mode=CacheMode.Table, engine=None, optimize=False):
        obj_hash = ''
        obj_query = ''
        if engine is None:
            engine = vulkn.engines.Memory()
        if isinstance(obj, str):
            obj_hash = hashlib.md5(obj.encode()).hexdigest()
            obj_query = obj
        if isinstance(obj, VulknCachedObject):
            return obj
        if mode == CacheMode.Table:
            intermediate_cache = self._create_table_cache(obj_hash, obj_query, engine)
            self._cache.append(intermediate_cache)
            return intermediate_cache.ref
        if mode == CacheMode.Array:
            intermediate_cache = self._store_array_vector(obj_hash, obj_query)
            self._cache.append(intermediate_cache)
            return intermediate_cache.ref
        stored_object = self._store_object(obj_hash, obj_query, optimize)
        return stored_object.ref


class VulknCachedObject:
    def __init__(self, ref, source, ttl=TTL.Session, mode=CacheMode.Table):
        self.ref = ref
        self.source = source
        self.ttl = ttl
        self.mode = mode

    def column_info(self, ctx):
        table_name = self.ref
        sql = f"SELECT name, type FROM system.columns WHERE database || '.' || table = '{table_name}'"
        return ctx.select(sql).to_record()
