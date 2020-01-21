# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import vulkn.engines
from vulkn import Vulkn
from vulkn.types.base import TypeBase, func, Literal
from vulkn.utils import timer


# TODO: Urgent - Fix before release. Add tests.


class ColumnVector(TypeBase):
    def __init__(self, value: any=None, name: str=None, n: str=None) -> None:
        if isinstance(value, Literal):
            self._value = value
        else:
            v = []
            for col in value:
                if isinstance(col, str):
                    v.append("'{}'".format(col))
                else:
                    v.append(str(col))
            self._value = Literal('SELECT arrayJoin([{}]) AS v'.format(','.join(v)))

    # Creation

    @classmethod
    def range(self, start, end, max_block_size=30000):
        q = f"""
            SELECT
                number AS i,
                number + {start} AS v 
            FROM numbers_mt(toUInt64(1 + abs({start} - {end})))
            SETTINGS max_block_size={max_block_size}"""
        return ColumnVector(Literal(q))

    @classmethod
    def rand(self, start, end, length, max_block_size=30000):
        q = f"""
            SELECT
                number AS i,
                {start} + rand64(number)%toUInt64(1 + abs({start} - {end})) AS v
            FROM numbers_mt({length})
            SETTINGS max_block_size={max_block_size}"""
        return ColumnVector(Literal(q))

    @classmethod
    def norm(self, mean, stddev, count):
        count = int(count)
        UInt32_MAX = vulkn.types.UInt32.MAX
        q = f"""
            SELECT
                rowNumberInAllBlocks() AS i,
                v
            FROM (
            SELECT
                arrayJoin(
                    arraySlice(
                        arrayReduce(
                            'groupArrayArray',
                            arrayMap(
                                i -> 
                                    [ ((sqrt(-2.0*log(rand(i)/{UInt32_MAX}))*cos(2*pi()*rand(i+100000000)/{UInt32_MAX}))*toFloat32({stddev}))+toFloat32({mean})
                                    , ((sqrt(-2.0*log(rand(i)/{UInt32_MAX}))*sin(2*pi()*rand(i+100000000)/{UInt32_MAX}))*toFloat32({stddev}))+toFloat32({mean})]
                                , range(toUInt64(ceil({count}/2))))), 1, {count})) AS v
            SETTINGS max_block_size=1)"""
        return ColumnVector(Literal(q))

    @classmethod
    def fromquery(self, query, column='v'):
        return ColumnVector(
            Literal(f"SELECT rowNumberInAllBlocks() AS i, {column} AS v FROM ({query})"))

    # Conversion

    def toArrayVector(self):
        from vulkn.types.array_vector import ArrayVector
        cache_table = self._cache()
        q = f"""
            SELECT
                groupArray(v) AS v
            FROM (
                SELECT v FROM {cache_table} WHERE i < 100000000 ORDER BY i LIMIT 100000000
            )"""
        return ArrayVector(Literal(q))

    # Manage

    def _cache(self, engine=None):
        ctx = Vulkn()
        engine = engine or vulkn.engines.Memory()
        return ctx.session.cache(self.sql, engine=engine)

    def alias(self, alias):
        self.vector_name = alias
        return self

    as_ = alias

    @timer
    def cache(self, engine=None):
        cache_table = self._cache(engine=engine)
        return ColumnVector(Literal(f'SELECT * FROM {cache_table}'))

    @timer
    def exec(self):
        ctx = Vulkn()
        return ctx._conn.select(self.sql)

    @timer
    def show(self, count=10, max_block_size=30000):
        ctx = Vulkn()
        sql = self.sql
        q = f'SELECT i, v FROM ({sql}) WHERE i <= {count} ORDER BY i LIMIT {count} SETTINGS max_block_size={max_block_size}'
        return ctx._conn.select(q).show()

    @timer
    def peek(self, count=10, max_block_size=30000):
        ctx = Vulkn()
        sql = self.sql
        q = f'SELECT i, v FROM ({sql}) WHERE i <= {count} ORDER BY i LIMIT {count} SETTINGS max_block_size={max_block_size}'
        return ctx._conn.select(q).to_records()

    def cast(self, to_type):
        vector = None
        toType = to_type if isinstance(to_type, str) else to_type.CAST
        if isinstance(self._value, list):
            vector = 'SELECT rowNumberInAllBlocks() AS i, arrayJoin({}) AS v'.format(str(self._value))
        else:
            vector = self.sql
        q = "SELECT i, cast(v, '{type}') AS v FROM ({vector})"
        return ColumnVector(Literal(q.format(type=toType, vector=vector)))

    # Operations

    def _cache_vector(self, cache):
        return self._cache() if cache else '({})'.format(str(self._value))

    def agg(self, agg):
        ctx = Vulkn()
        q = 'SELECT {agg}(v) AS {agg} FROM ({vector})'
        return ctx._conn.select(q.format(agg=agg, vector=self.sql)).to_records()

    def cut(self, cut_length, cache=False):
        vector = self._cache_vector(cache)
        q = f"""
            SELECT (i-i%{cut_length})/{cut_length} AS i, groupArray(v) AS v
            FROM ({vector})
            GROUP BY i ORDER BY i"""
        return ColumnVector(Literal(q))

    def delta(self, cache=False):
        vector = self._cache_vector(cache)
        q = f"SELECT i, runningDifference(v) AS v FROM (SELECT i, v FROM {vector} ORDER BY i)"
        return ColumnVector(Literal(q))

    def flatten(self, cache=False):
        vector = self._cache_vector(cache)
        q = f"""
            SELECT rowNumberInAllBlocks() AS i, _v AS v
            FROM (
                SELECT _v FROM ({vector}) 
                ARRAY JOIN arrayEnumerate(v) AS _i, v AS _v
                ORDER BY i, _i
            )"""
        return ColumnVector(Literal(q))

    def join(self, other, cache=False):
        vector = self._cache_vector(cache)
        other_vector = other._cache_vector(cache)
        q = f"""
            SELECT rowNumberInAllBlocks() AS i, v
            FROM (
                SELECT v FROM ({vector}) ORDER BY i
                UNION ALL
                SELECT v FROM ({other_vector}) ORDER BY i
            )"""
        return ColumnVector(Literal(q))

    def index_agg(self, agg):
        ctx = Vulkn()
        q = 'SELECT {agg}(i) AS {agg} FROM ({vector})'
        return ctx._conn.select(q.format(agg=agg, vector=self.sql)).to_records()    

    def limit(self, length, cache=False):
        vector = self._cache_vector(cache)
        return ColumnVector(Literal(f'SELECT * FROM ({vector}) LIMIT {length}'))

    def map(self, func, *args, cache=False):
        vector = self._cache_vector(cache)
        arg_list = '{},'.format(','.join(list(map(str, args)))) if len(args) > 0 else ''
        q = f'SELECT i, {func}({arg_list}v) AS v FROM ({vector})'
        return ColumnVector(Literal(q))

    def maplag(self, func, cache=False):
        vector = self._cache_vector(cache)
        q = f"""
            SELECT i, {func}(v1.v, v2.v) AS v FROM ({vector}) v1
            ALL INNER JOIN (
                SELECT toUInt64(i-1) AS i, v FROM ({vector})
            ) v2 USING (i)"""
        return ColumnVector(Literal(q))

    def maplead(self, func, cache=False):
        vector = self._cache_vector(cache)
        q = f"""
            SELECT i, {func}(v2.v, v1.v) AS v FROM ({vector}) v1
            ALL INNER JOIN (
                SELECT toUInt64(i-1) AS i, v FROM ({vector})
            ) v2 USING (i)"""
        return ColumnVector(Literal(q))

    def next(self, cache=False):
        vector = self._cache_vector(cache)
        q = f"""
            SELECT i, v FROM ({vector}) WHERE i > 0
            UNION ALL
            SELECT (SELECT COUNT() FROM {vector}), NULL"""
        return ColumnVector(Literal(q))

    def prev(self, cache=False):
        vector = self._cache_vector(cache)
        q = f"""
            SELECT 0 AS i, NULL AS v
            UNION ALL
            SELECT i+1, v FROM (
                SELECT * FROM ({vector}) WHERE i < (SELECT max(i-1) FROM ({vector}))
            )"""
        return ColumnVector(Literal(q))

    def reverse(self, cache=False):
        vector = self._cache_vector(cache)
        q = f"SELECT rowNumberInAllBlocks() AS i, v FROM (SELECT v FROM {vector} ORDER BY v DESC)"
        return ColumnVector(Literal(q))

    def shuffle(self, cache=False):
        vector = self._cache_vector(cache)
        q = f"SELECT rowNumberInAllBlocks() AS i, v FROM {vector} ORDER BY rand()"
        return ColumnVector(Literal(q))

    def sort(self, cache=False):
        vector = self._cache_vector(cache)
        q = f"SELECT rowNumberInAllBlocks() AS i, v FROM (SELECT v FROM {vector} ORDER BY v)"
        return ColumnVector(Literal(q))

    sort_reverse = reverse    

    def take(self, length):
        vector = None
        if isinstance(self._value, str) or isinstance(self._value, Literal):
            vector = 'SELECT groupArray(v) FROM (SELECT v FROM ({}) ORDER BY i)'.format(self.sql)
        else:
            vector = str(self)
        q = f"""
            SELECT rowNumberInAllBlocks() AS i, v
            FROM (
                WITH ({vector}) AS `#v`
                SELECT `#v`[(number%length(`#v`))+1] AS v
                FROM numbers_mt({length})
            )"""
        return ColumnVector(Literal(q))
