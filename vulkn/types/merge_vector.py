# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import random
import math
import hashlib
import os


import vulkn
from vulkn.types.base import func, Literal
from vulkn.utils import timer


class MergeVector:
    def __init__(self, max_block_size=10000, max_threads=2, array_chunk_size=100000000, uuid=None):
        if array_chunk_size > 100000000:
            raise Exception('array_chunk_size cannot be greater than 100 million')
        self._ref = None
        self._arrays = None
        self._max_block_size = max_block_size
        self._max_threads = max_threads
        self._array_chunk_size = array_chunk_size
        self._uuid = uuid or MergeVector.generateUUID()
        self._length = None
        self._type = 'UInt64'
        self._sorted = False

    def toArrayVector(self):
        from vulkn.types.array_vector import ArrayVector
        return ArrayVector(
            Literal(
                "SELECT v FROM {} WHERE i < 100000000 ORDER BY _table, i LIMIT 100000000".format(
                    self._ref)))

    def _session(self):
        return vulkn.Vulkn().session.session_store

    def _rebuild_arrays(self):
        ctx = vulkn.Vulkn()
        rename = [f'RENAME TABLE {chunk}_ TO {chunk}' for chunk in self._arrays]
        drop = [f'DROP TABLE IF EXISTS {chunk}' for chunk in self._arrays]
        ctx.scheduler.dispatch(drop)
        ctx.scheduler.dispatch(rename)

    def _rebuild_ref(self):
        ctx = vulkn.Vulkn()
        parent = "CREATE TABLE {ref} AS {ref}_1 ENGINE = Merge('{vulkn_database}', '^{session}_{uuid}_([0-9]*)$')"
        ctx.scheduler.dispatch('DROP TABLE IF EXISTS {ref}'.format(ref=self._ref))
        ctx.scheduler.dispatch(parent.format(ref=self._ref, 
                                             vulkn_database=self._session().split('.')[0],
                                             session=self._session().split('.')[1],
                                             uuid=self._uuid))

    @staticmethod
    def generateUUID():
        return hashlib.md5(str(random.random()).encode()).hexdigest()

    def chunks(self, length, chunk_size):
        r = [math.floor(length/chunk_size), length%chunk_size]
        if r[0] == 1 and r[1] == 0 and self._length is not None:
            r[1] = length/self._length
        return r

    def __getattr__(self, attrname):
        attrs = [
            'count', 'min','max','median','avg','sum','any','anyHeavy','anyLast','skewPop','skewSamp',
            'kurtPop','kurtSamp','uniq','uniqCombined','uniqExact','varSamp','varPop','stddevSamp',
            'stddevPop']
        if attrname in attrs:
            return lambda: self.agg(attrname)
        else:
            raise AttributeError

    @classmethod
    @timer
    #def rand(self, min_value, max_value, length, max_block_size=10000, max_threads=2, array_chunk_size=5000000):
    def rand(self, min_value, max_value, length, max_block_size=None, max_threads=2, array_chunk_size=None):
        sql = 'CREATE TABLE {session}_{uuid}_{chunk} ENGINE=Memory() AS '
        sql += 'SELECT number AS i, rand64()%toUInt64({mod}) AS v FROM numbers_mt({array_chunk_size}) '
        sql += 'SETTINGS max_block_size={max_block_size}, max_threads={max_threads}'
        array_chunk_size = array_chunk_size or math.ceil(length/((os.cpu_count()*0.75)-2))
        if array_chunk_size > 100000000:
            array_chunk_size = 100000000
        max_block_size = max_block_size or array_chunk_size
        uuid = MergeVector.generateUUID()
        r = MergeVector(uuid=uuid,
                        max_block_size=max_block_size,
                        max_threads=max_threads,
                        array_chunk_size=array_chunk_size)
        r._ref = '{session}_{uuid}'.format(session=r._session(), uuid=uuid)
        modsize = 1 + abs(min_value - max_value)
        chunks = r.chunks(length, array_chunk_size)
        queries = []
        arrays = []
        for i in range(chunks[0]):
            chunk = i+1
            queries.append(sql.format(session=r._session(),
                                      uuid=uuid,
                                      chunk=chunk,
                                      mod=modsize,
                                      array_chunk_size=array_chunk_size,
                                      max_block_size=max_block_size,
                                      max_threads=max_threads))
            arrays.append('{session}_{uuid}_{chunk}'.format(session=r._session(),
                                                            uuid=uuid,
                                                            chunk=chunk))
        if chunks[1] > 0:
            arrays.append('{session}_{uuid}_{chunk}'.format(session=r._session(),
                                                            uuid=uuid,
                                                            chunk=len(queries)+1))
            queries.append(sql.format(session=r._session(),
                                      uuid=uuid,
                                      chunk=len(queries)+1,
                                      mod=modsize,
                                      array_chunk_size=chunks[1],
                                      max_block_size=max_block_size,
                                      max_threads=max_threads))
        ctx = vulkn.Vulkn()
        ctx.scheduler.dispatch(queries)
        ctx.session._cache.extend(arrays)
        ctx.session._cache.append(r._ref)
        r._arrays = arrays
        r._rebuild_ref()
        r._length = length
        return r
    
    @classmethod
    @timer
    #def rand(self, min_value, max_value, length, max_block_size=10000, max_threads=2, array_chunk_size=5000000):
    def range(self, start_value, end_value, max_block_size=None, max_threads=2, array_chunk_size=100000000):
        sql = 'CREATE TABLE {session}_{uuid}_{chunk} ENGINE=Memory() AS '
        sql += 'SELECT number AS i, number+({array_chunk_size}*{idx}) AS v FROM numbers_mt({array_chunk_size}) '
        sql += 'SETTINGS max_block_size={max_block_size}, max_threads={max_threads}'
        queries = []
        arrays = []
        uuid = MergeVector.generateUUID()
        max_block_size = max_block_size or array_chunk_size
        r = MergeVector(uuid=uuid,
                        max_block_size=max_block_size,
                        max_threads=max_threads,
                        array_chunk_size=array_chunk_size)
        r._ref = '{session}_{uuid}'.format(session=r._session(), uuid=uuid)
        length = abs(end_value - start_value)
        chunks = r.chunks(length, array_chunk_size)
        for i in range(chunks[0]):
            chunk = i+1
            queries.append(sql.format(session=r._session(),
                                      uuid=uuid,
                                      chunk=chunk,
                                      idx=i,
                                      array_chunk_size=array_chunk_size,
                                      max_block_size=max_block_size,
                                      max_threads=max_threads))
            arrays.append('{session}_{uuid}_{chunk}'.format(session=r._session(),
                                                            uuid=uuid,
                                                            chunk=chunk))
        if chunks[1] > 0:
            arrays.append('{session}_{uuid}_{chunk}'.format(session=r._session(),
                                                            uuid=uuid,
                                                            chunk=len(queries)+1))
            queries.append(sql.format(session=r._session(),
                                      uuid=uuid,
                                      chunk=len(queries)+1,
                                      idx=chunks[0],
                                      array_chunk_size=chunks[1],
                                      max_block_size=max_block_size,
                                      max_threads=max_threads))
        ctx = vulkn.Vulkn()
        ctx.scheduler.dispatch(queries)
        ctx.session._cache.extend(arrays)
        ctx.session._cache.append(r._ref)
        r._arrays = arrays
        r._rebuild_ref()
        r._length = length
        r._sorted = True
        return r

    def agg(self, agg_func):
        return vulkn.Vulkn().q('SELECT {agg_func}(v) FROM {vector}'.format(agg_func=agg_func,
                                                                           vector=self._ref))

    @timer
    def cast(self, to_type):
        sql = 'CREATE TABLE {chunk}_ ENGINE = Memory() AS '
        sql += "SELECT i, cast(v, '{type}') AS v FROM {chunk} "
        sql += 'SETTINGS max_block_size={max_block_size}, max_threads={max_threads}'
        toType = to_type if isinstance(to_type, str) else to_type.CAST
        queries = []
        for a in self._arrays:
            queries.append(sql.format(chunk=a,
                                      type=toType,
                                      max_block_size=self._max_block_size,
                                      max_threads=self._max_threads))
        vulkn.Vulkn().scheduler.dispatch(queries)
        self._rebuild_arrays()
        self._rebuild_ref()
        self._type = toType
        self._sorted = False
        return self

    @timer
    def shuffle(self):
        sql = 'CREATE TABLE {chunk}_ ENGINE = Memory() AS '
        sql += "SELECT rowNumberInBlock() AS i, v FROM {chunk} ORDER BY rand() "
        sql += 'SETTINGS max_block_size={max_block_size}, max_threads={max_threads}'
        queries = []
        for a in self._arrays:
            queries.append(sql.format(chunk=a,
                                      max_block_size=self._max_block_size,
                                      max_threads=self._max_threads))
        vulkn.Vulkn().scheduler.dispatch(queries)
        self._rebuild_arrays()
        self._sorted = False
        return self

    def stats(self):
        sql = 'SELECT min(v) AS min, max(v) AS max, avg(v) AS avg, median(v) AS median FROM {vector}'
        return vulkn.Vulkn().q(sql.format(vector=self._ref))

    def quantiles(self):
        cols = ['quantile({})(v)'.format(str((x+1)/len(self._arrays))) for x in range(len(self._arrays))]
        sql = 'SELECT arrayJoin([{quantiles}]) AS histogram FROM {vector}'
        return vulkn.Vulkn().q(sql.format(quantiles=','.join(cols), vector=self._ref))

    @timer
    def sort(self):
        if self._sorted:
            return self
        if self._type == 'String':
            raise Exception('Supporting for sorting Strings is currently not available in MergeVectors')
        ranges = [h['histogram'] for h in self.quantiles().exec().to_records()]
        queries = []
        for i, a in enumerate(ranges):
            sql = 'CREATE TABLE {chunk}_ ENGINE = Memory() AS '
            sql += 'SELECT rowNumberInBlock() AS i, v FROM (SELECT v FROM {vector} WHERE '
            if i == 0:
                sql += "v < {max_bound} ORDER BY v) "
            elif i == len(self._arrays) - 1:
                sql += "v >= {min_bound} ORDER BY v) "
            else:
                sql += "v >= {min_bound} AND v < {max_bound} ORDER BY v) "
            sql += 'SETTINGS max_block_size={max_block_size}, max_threads={max_threads}'
            queries.append(sql.format(chunk='{chunk}_{idx}'.format(chunk=self._ref, idx=i+1),
                                      max_block_size=round(self._array_chunk_size*1.2),
                                      max_threads=self._max_threads,
                                      vector=self._ref,
                                      max_bound=a,
                                      min_bound=ranges[i-1]))
        vulkn.Vulkn().scheduler.dispatch(queries)
        self._rebuild_arrays()
        self._sorted = True
        return self

    def peek(self):
        sql = 'SELECT * FROM {vector}_1 WHERE i < 20 ORDER BY i LIMIT 20'
        return vulkn.Vulkn().q(sql.format(vector=self._ref))

    @timer
    def take(self, num_rows):
        # TODO: This uses too much memory for large values (1 billion..).
        sql = """
            CREATE TABLE {session}_{new_uuid}_{new_chunk} ENGINE=Memory() AS 
            SELECT
                rowNumberInAllBlocks() AS i, 
                v
            FROM (
                WITH
                    (SELECT groupArray(v) FROM (SELECT v FROM {session}_{uuid}_{chunk} ORDER BY i)) AS `#v`
                SELECT `#v`[(number%length(`#v`))+1] AS v FROM numbers_mt(100000000)
            )"""
        r = MergeVector(max_block_size=self._max_block_size,
                        max_threads=self._max_threads,
                        array_chunk_size=self._array_chunk_size)
        r._length = num_rows
        r._ref = '{session}_{uuid}'.format(session=r._session(), uuid=r._uuid)
        arrays = []
        queries = []
        chunk = 0
        chunks = r.chunks(num_rows, self._array_chunk_size)
        for i in range(chunks[0]):
            new_chunk = i+1
            chunk = (i+1)%len(self._arrays)
            chunk = 1 if chunk == 0 else chunk
            queries.append(sql.format(session=r._session(),
                                      new_uuid=r._uuid,
                                      uuid=self._uuid,
                                      new_chunk=new_chunk,
                                      chunk=chunk,
                                      max_block_size=self._max_block_size,
                                      max_threads=self._max_threads))
            arrays.append('{session}_{uuid}_{chunk}'.format(session=r._session(),
                                                            uuid=r._uuid,
                                                            chunk=new_chunk))
        if (chunks[1] > 0 or 
                (self._array_chunk_size >= self._length and self._array_chunk_size >= num_rows)):
            sql += ' LIMIT {length}'.format(length=chunks[1] if chunks[1] > 0 else num_rows)
            arrays.append('{session}_{uuid}_{chunk}'.format(session=r._session(),
                                                            uuid=r._uuid,
                                                            chunk=len(queries)+1))
            queries.append(sql.format(session=r._session(),
                                      new_uuid=r._uuid,
                                      uuid=self._uuid,
                                      new_chunk=len(queries)+1,
                                      chunk=1 if len(self._arrays) == 1 else (chunk+1)%len(self._arrays),
                                      max_block_size=self._max_block_size,
                                      max_threads=self._max_threads))
        ctx = vulkn.Vulkn()
        ctx.scheduler.dispatch(queries)
        ctx.session._cache.extend(arrays)
        ctx.session._cache.append(r._ref)
        r._arrays = arrays
        r._rebuild_ref()
        return r
