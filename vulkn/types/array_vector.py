# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import uuid


import vulkn
from vulkn import Vulkn, session
from vulkn.utils import timer
from vulkn.types.base import TypeBase, func, Literal


# TODO: Urgent - Fix before release.


class ArrayVector(TypeBase):
    def __init__(self, value: any=None, name: str=None, n: str=None) -> None:
        self._sorted = False
        self._cache_table = None
        if isinstance(value, Literal):
            self._value = value
        else:
            v = []
            for col in value:
                if isinstance(col, str):
                    v.append("'{}'".format(col))
                else:
                    v.append(str(col))
            self._value = Literal("SELECT [{}] AS v".format(','.join(v)))

    # Creation

    @classmethod
    def range(self, start, end):
        if end - start > 100000000:
            raise Exception('ArrayVector cannot contain more than 100 million elements')
        q = f"""
            SELECT
                groupArray(number + {start}) AS v
            FROM numbers(toUInt64(1 + abs({start} - {end})))
            SETTINGS max_block_size = 100000000"""
        r = ArrayVector(Literal(q))
        r._sorted = True
        return r

    @classmethod
    def rand(self, start, end, length):
        if length > 100000000:
            raise Exception('ArrayVector cannot contain more than 100 million elements')
        q = f"""
            SELECT 
                groupArray({start} + rand64(number)%toUInt64(1 + abs({start} - {end}))) AS v
            FROM numbers({length})
            SETTINGS max_block_size = 100000000"""
        return ArrayVector(Literal(q))

    @classmethod
    def norm(self, mean, stddev, length):
        if length > 100000000:
            raise Exception('ArrayVector cannot contain more than 100 million elements')
        count = int(length)
        UInt32_MAX = vulkn.types.UInt32.MAX
        q = f"""
            SELECT
                arraySlice(
                    arrayReduce(
                        'groupArrayArray',
                        arrayMap(
                            i -> 
                                [ ((sqrt(-2.0*log(rand(i)/{UInt32_MAX}))*cos(2*pi()*rand(i+100000000)/{UInt32_MAX}))*toFloat32({stddev}))+toFloat32({mean})
                                , ((sqrt(-2.0*log(rand(i)/{UInt32_MAX}))*sin(2*pi()*rand(i+100000000)/{UInt32_MAX}))*toFloat32({stddev}))+toFloat32({mean})]
                            , range(toUInt64(ceil({count}/2))))), 1, {count}) AS v"""
        return ArrayVector(Literal(q))

    @classmethod
    def fromquery(self, query, column='v'):
        q = f"SELECT groupArray({column}) AS v FROM ({query}) SETTINGS max_block_size = 100000000"
        return ArrayVector(Literal(q))

    # Conversion

    def toColumnVector(self):
        from vulkn.types.column_vector import ColumnVector
        cache_table = self._cache()
        q = f"""
            SELECT i, _v AS v
            FROM (
                SELECT i, _v
                FROM ({cache_table})
                ARRAY JOIN
                    arrayEnumerate(v) AS i,
                    v AS _v)"""
        return ColumnVector(Literal(q))

    # Manage

    def alias(self, alias):
        self.vector_name = alias
        return self

    as_ = alias

    def _cache(self):
        ctx = Vulkn()
        return ctx.session.cache(self.sql, mode=session.CacheMode.Array)

    @timer
    def cache(self):
        cache_table = self._cache()
        r = ArrayVector(Literal("SELECT v FROM {}".format(cache_table)))
        r._sorted = self._sorted
        r._cache_table = cache_table
        return r

    def cast(self, to_type):
        toType = to_type if isinstance(to_type, str) else to_type.CAST
        q = "SELECT cast(v, 'Array({type})') AS v FROM ({vector})"
        r = ArrayVector(Literal(q.format(type=toType, vector=self.sql)))
        r._sorted = self._sorted
        return r

    @timer
    def exec(self):
        ctx = Vulkn()
        return ctx._conn.select(str(self.sql))

    @timer
    def show(self, count=10, max_block_size=30000):
        ctx = Vulkn()
        sql = self.sql
        q = f"""
            SELECT
                _i AS i,
                _v AS v
            FROM (
                SELECT
                    _i, _v
                FROM ({sql})
                ARRAY JOIN
                    arrayEnumerate(arraySlice(v, 1, {count})) AS _i,
                    arraySlice(v, 1, {count}) AS _v
            ) SETTINGS max_block_size={max_block_size}"""
        return ctx._conn.select(q).show()

    @timer
    def peek(self, count=10, max_block_size=30000):
        ctx = Vulkn()
        sql = self.sql
        q = f"""
            SELECT
                _i AS i,
                _v AS v
            FROM (
                SELECT
                    _i, _v
                FROM ({sql})
                ARRAY JOIN
                    arrayEnumerate(arraySlice(v, 1, {count})) AS _i,
                    arraySlice(v, 1, {count}) AS _v
            ) SETTINGS max_block_size={max_block_size}"""
        return ctx._conn.select(q).to_records()

    # Operations

    @timer
    def agg(self, agg):
        ctx = Vulkn()
        vector = self.sql
        q = f"SELECT arrayReduce('{agg}', v) AS v FROM ({vector})"
        return ctx._conn.select(q).to_records()

    def cut(self, cut_length):
        vector = self._value
        q = f"""
            SELECT
                groupArray(_v) AS v
            FROM (
                WITH
                    (_i-_i%{cut_length})/{cut_length}+1 AS _idx
                SELECT groupArray(_cut) AS _v
                FROM (
                    SELECT i - 1 AS _i, _cut FROM ({vector}) ARRAY JOIN v AS _cut, arrayEnumerate(v) AS i
                )
                GROUP BY _idx ORDER BY _idx
            ) SETTINGS max_block_size = 100000000"""
        r = ArrayVector(Literal(q))
        r._sorted = self._sorted
        return r

    def delta(self):
        vector = self._value
        q = f"""
            SELECT arrayConcat([NULL], groupArray(_delta)) AS v
            FROM (
                SELECT
                    v1 - v2 AS _delta
                FROM ({vector})
                ARRAY JOIN
                    v AS v1,
                    arrayConcat([NULL], arraySlice(v, 1, -1)) AS v2
            ) SETTINGS max_block_size = 100000000"""
        return ArrayVector(Literal(q))

    def flatten(self):
        return ArrayVector(
            Literal("SELECT groupArrayArrayArray(v) AS v FROM ({})".format(self._value)))

    @timer
    def index_agg(self, agg):
        ctx = Vulkn()
        vector = self.sql
        q = f"SELECT arrayReduce('{agg}', arrayEnumerate(v)) AS v FROM ({vector})"
        return ctx._conn.select(q).to_records()

    def join(self, N):
        vector = self._value
        other_vector = N._value
        q = f"""
            SELECT groupArray(_v) AS v
            FROM (
                SELECT _v FROM ({vector}) ARRAY JOIN v AS _v
                UNION ALL
                SELECT _v FROM ({other_vector}) ARRAY JOIN v AS _v
            ) SETTINGS max_block_size=100000000"""
        #q = "SELECT arrayConcat(({}),({})) AS v".format(self._value, N._value)
        return ArrayVector(Literal(q))

    def map(self, func, *args):
        a = ','.join(list(map(str, args))) + ',' if len(args) > 0 else ''
        vector = self.sql
        q = f"""
            SELECT groupArray(_v) AS v
            FROM (
                SELECT
                    {func}({a}_map) AS _v
                FROM ({vector})
                ARRAY JOIN
                    v AS _map
            ) SETTINGS max_block_size = 100000000"""
        return ArrayVector(Literal(q))

    def maplag(self, func):
        vector = self.sql
        q = f"""
            SELECT groupArray(_maplag) AS v
            FROM (
                SELECT
                    {func}(v2, v1) AS _maplag
                FROM ({vector})
                ARRAY JOIN
                    v AS v1,
                    arrayConcat([NULL], arraySlice(v, 1, -1)) AS v2
            ) SETTINGS max_block_size = 100000000"""
        return ArrayVector(Literal(q))

    def maplead(self, func):
        vector = self.sql
        q = f"""
            SELECT groupArray(_maplead) AS v
            FROM (
                SELECT
                    {func}(v2, v1) AS _maplead
                FROM ({vector})
                ARRAY JOIN
                    v AS v1,
                    arrayConcat(arraySlice(v, 2), [NULL]) AS v2
            ) SETTINGS max_block_size = 100000000"""
        return ArrayVector(Literal(q))

    def move(self, positions):
        vector = self._value
        q = None
        if positions > 0:
            q = f"""
                SELECT 
                    arrayConcat(
                        arrayWithConstant({positions}, NULL),
                        arraySlice(v, 1, -({positions}))
                    ) AS v
                FROM ({vector})"""
        elif positions < 0:
            q = f"""
                SELECT
                    arrayConcat(
                        arraySlice(v, abs({positions})+1),
                        arrayWithConstant(abs({positions}), NULL)
                    ) AS v
                FROM ({vector})"""
        else:
            return self
        r = ArrayVector(Literal(q))
        r._sorted = self._sorted
        return r

    def next(self):
        vector = self._value
        q = f"SELECT arrayConcat(arraySlice(v, 2), [NULL]) AS v FROM ({vector})"
        r = ArrayVector(Literal(q))
        r._sorted = self._sorted
        return r

    def prev(self):
        vector = self._value
        q = f"SELECT arrayConcat([NULL], arraySlice(v, 1, -1)) AS v FROM ({vector})"
        r = ArrayVector(Literal(q))
        r._sorted = self._sorted
        return r

    def shuffle(self):
        vector = self._value
        q = f"""
            SELECT
                groupArray(_shuffle) AS v
            FROM (
                SELECT _shuffle FROM (
                    SELECT _shuffle FROM ({vector}) ARRAY JOIN v AS _shuffle
                ) ORDER BY rand()
            ) SETTINGS max_block_size = 100000000"""
        return ArrayVector(Literal(q))

    def sort(self):
        if self._sorted:
            return self
        vector = self.sql
        q = f"""
            SELECT
                groupArray(_sort) AS v
            FROM (
                SELECT _sort FROM (
                    SELECT _sort FROM ({vector}) ARRAY JOIN v AS _sort
                ) ORDER BY _sort
            ) SETTINGS max_block_size = 100000000"""
        r = ArrayVector(Literal(q))
        r._sorted = True
        return r

    def sort_reverse(self):
        vector = self.sql
        q = f"SELECT arrayReverseSort(v) AS v FROM ({vector})"
        return ArrayVector(Literal(q))
  
    reverse = sort_reverse    

    def take(self, length):
        if length > 100000000:
            raise Exception('ArrayVector cannot contain more than 100 million elements')
        vector = self._value
        q = f"""
            SELECT
                _take AS v
            FROM (
                SELECT
                    groupArrayArrayArrayArray([
                        arrayMap(x -> v, range(toUInt64(floor({length} / length(v))))),
                        [arraySlice(v, 1, {length} % length(v))]
                    ]) AS _take
                FROM ({vector}))"""
        return ArrayVector(Literal(q))