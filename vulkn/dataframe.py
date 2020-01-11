# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import copy
import logging
from functools import partial


import vulkn.session
from vulkn.clickhouse import sqlformat
from vulkn.utils import VulknSQLFormatter, timer, LogLevels


log = logging.getLogger()


# TODO: Next release. Add table function dataframes:
# https://clickhouse.yandex/docs/en/query_language/table_functions/


def copy_set(obj, key, *value):
    bool_keys = ['_distinct']
    this = copy.deepcopy(obj)
    if key in bool_keys:
        setattr(this, key, True)
    else:
        setattr(this, key, value)
    return this


class WriteMode:
    Replace = 0
    Append = 1
    Create = 2


class JoinStrictness:
    Any='ANY'
    All='ALL'
    AsOf='ASOF'
    Default=''


class JoinType:
    Left='LEFT'
    Right='RIGHT'
    LeftInner='LEFT INNER'
    RightInner='RIGHT INNER'
    Inner='INNER'
    Join=''
    LeftOuter='LEFT OUTER'
    RightOuter='RIGHT OUTER'
    Full='FULL'
    FullOuter='FULL OUTER'
    Cross='CROSS'


class VulknDataFrame:   
    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == '_ctx':
                setattr(result, k, v)
            else:
                setattr(result, k, copy.deepcopy(v, memo))
        return result


def JoinDataFrame(
        ctx, jointype, left, right, keys=None, strictness=JoinStrictness.All, global_mode=False):
    j = '({left}) {global_mode} {strictness} {join_type} JOIN ({right})'
    q = j.format(left=left._get_query(), 
                 global_mode='GLOBAL' if global_mode else '',
                 strictness=strictness,
                 join_type=jointype,
                 right=right._get_query())
    if keys:
        q = '{} USING ({})'.format(q, ','.join(keys))
    return SelectQueryDataFrame(ctx, q).select('*')


def NumbersDataFrame(ctx, count, system=False, mt=False):
    if system:
        t = 'system.numbers' + ('_mt' if mt else '')
        return SelectQueryDataFrame(ctx, t).limit(count).select('*')
    else:
        t = 'numbers' + ('_mt' if mt else '')
        return SelectQueryDataFrame(ctx, '{}({})'.format(t, count)).select('*')


def RandomDataFrame(ctx, count, start=0, end=18446744073709551615, system=False, mt=False):
    q = f'{start} + rand()%(if(mod == 0, mod - 1, ({end}-({start})+1) AS mod)) AS number'
    if system:
        t = 'system.numbers' + ('_mt' if mt else '')
        return SelectQueryDataFrame(ctx, t).limit(count).select(q)
    else:
        t = 'numbers' + ('_mt' if mt else '')
        return SelectQueryDataFrame(ctx, '{}({})'.format(t, count)).select(q)


def RandomFloatDataFrame(ctx, count, start=0, end=18446744073709551615, system=False, mt=False):
    q = f"{start} + rand64()%({end}-({start})) + rand64()/18446744073709551615 AS number"
    if system:
        t = 'system.numbers' + ('_mt' if mt else '')
        return SelectQueryDataFrame(ctx, t).limit(count).select(q)
    else:
        t = 'numbers' + ('_mt' if mt else '')
        return SelectQueryDataFrame(ctx, '{}({})'.format(t, count)).select(q)


def OneDataFrame(ctx):
    return SelectQueryDataFrame(ctx, 'system.one').select('*')


def RangeDataFrame(ctx, start, end, system=False, mt=False):
    if end <= start:
        raise Exception('end must be greater than start')
    if system or mt:
        t = 'system.numbers' + ('_mt' if mt else '')
        return (SelectQueryDataFrame(ctx, t)
                .limit(end + 1 -(start))
                .select('number + {} AS range'.format(str(start))))
    else:
        return (SelectQueryDataFrame(ctx, 'numbers({})'.format(end + 1 -(start)))
                .select('number + {} AS range'.format(str(start))))


def aj(dataframes, keys, global_mode=False):
    df = dataframes[0]
    for d in dataframes:
        df = df.aj(d, keys, global_mode)
    return df


class ShowSQLMixin:
    def _show_sql(self, **params):
        q = self._get_query()
        sql = VulknSQLFormatter().format(q, **params) if params else q
        return sql
 
    def show_sql(self, **params):
        q = self._get_query()
        sql = VulknSQLFormatter().format(q, **params) if params else q
        statements = vulkn.sql.SQLMessage(sql).statements()
        if len(statements) > 1:
            raise Exception('More than one statement is not supported')
        return sqlformat(statements[0].optimize())


class CachedQueryMixin:
    def cache(self, engine=None):
        if engine is None:
            engine = vulkn.engines.Memory()
        q = self._get_query()
        sql = VulknSQLFormatter().format(q, **self._params[0]) if self._params else q
        statements = vulkn.sql.SQLMessage(sql).statements()
        if len(statements) > 1:
            raise Exception('More than one statement is not supported')
        t = self._ctx.session.cache(statements[0].optimize(), engine=engine)
        return SelectQueryDataFrame(self._ctx, t).select('*')


class TableWriterMixin:
    def write(self, database, table, engine=None, mode=WriteMode.Create):
        table_exists = self._ctx.tableExists(database, table)
        if table_exists and mode == WriteMode.Create:
            raise Exception('Table exists and invalid write mode specified')
        if engine is None:
            engine = vulkn.engines.Memory()
        if mode != WriteMode.Append:
            self._ctx.dropTable(database, table)
        q = self._get_query()
        source = VulknSQLFormatter().format(q, **(self._params)) if self._params else q
        statements = vulkn.sql.SQLMessage(source).statements()
        if len(statements) > 1:
            raise Exception('More than one statement is not supported')
        sql = statements[0].optimize()
        if mode != WriteMode.Append:
            sql = f'CREATE TABLE {database}.{table} ENGINE = {engine} AS {sql}'
        else:
            sql = f'INSERT INTO {database}.{table} {sql}'
        if not self._ctx.exec(sql):
            raise Exception('Unable to write table')
        return SelectQueryDataFrame(self._ctx, f'{database}.{table}').select('*')


class QueryExecutorMixin:
    def plan(self, **params):
        q = self._get_query()
        statements = vulkn.sql.SQLMessage(VulknSQLFormatter().format(q, **params)).statements()
        if len(statements) > 1:
            raise Exception('More than one statement is not supported')
        return QueryStringDataFrame(self._ctx, statements[0].optimize()).select('*')

    @timer
    def exec(self, **params):
        q = self._get_query()
        statements = vulkn.sql.SQLMessage(VulknSQLFormatter().format(q, **params)).statements()
        if len(statements) > 1:
            raise Exception('More than one statement is not supported')
        return self._ctx._conn.select(statements[0].optimize())

    def to_records(self):
        return self.exec().to_records()

    def to_pandas(self):
        return self.exec().to_pandas()

    def show(self):
        return self.exec().show()

    r = property(to_records)
    s = property(show)
    p = property(to_pandas)
    e = exec


class BaseTableDataFrame:
    def __init__(self, ctx, database, table):
        self._ctx = ctx
        self._database = database
        self._table = table

    def __str__(self):
        return '"{database}"."{table}"'.format(database=self._database, table=self._table)

    def __getattr__(self, attrname):
        return getattr(SelectQueryDataFrame(self._ctx, str(self)), attrname)

    def desc(self):
        return self._ctx.q(f'DESC {self._database}.{self._table}').exec()


class QueryStringDataFrame(VulknDataFrame, QueryExecutorMixin, ShowSQLMixin, CachedQueryMixin, TableWriterMixin):
    def __init__(self, ctx, query):
        self._ctx = ctx
        self._query = query

    def _get_query(self):
        return self._query

    def __getattr__(self, attrname):
        attrs = [
            'limit','where','filter','limitby','head','first','distinct','orderby','sort','prewhere']
        this = SelectQueryDataFrame(self._ctx, '({})'.format(self._get_query()))
        if attrname.lower() in attrs:
            return getattr(this.select('*'), attrname)
        else:
            return getattr(this, attrname)


class SelectQueryDataFrame(VulknDataFrame,
                           QueryExecutorMixin,
                           ShowSQLMixin,
                           CachedQueryMixin,
                           TableWriterMixin):
    def __init__(self, ctx, source=None):
        self.max_rows = 100
        self.max_preview_rows = 30
        self._ctx = ctx
        self._columns = None
        self._distinct = False
        self._table = (source,) if source is not None else None
        self._prewhere = None
        self._where = None
        self._groupby = None
        self._orderby = None
        self._having = None
        self._limit = None
        self._limitby = None
        self._vectorizeby = None
        self._join = None
        self._with_ = None
        self._params = None

    def __getattr__(self, attrname):
        attrs = {
            'with_': None,
            'distinct': None, 
            #'table': None,
            'From': '_table',
            'from_': '_table',
            'preWhere': None,
            'where': None,
            'filter': '_where',
            'groupBy': None,
            'orderBy': None,
            'sort': '_orderby',
            'having': None,
            'limit': None,
            'params': None,
        }

        if attrname in attrs.keys():
            attr = attrs[attrname] or '_{}'.format(attrname.lower())
            return partial(copy_set, self, attr)
        else:
            raise AttributeError

    def all(self):
        cols = ('*',)
        if not isinstance(self._table[0], type(self)):
            table = self._table[0].rsplit('.')[1].strip('"')
            cols = [t._name for t in self._ctx.getSchema(table)]
        return self.select(*cols)

    def select(self, *cols):
        if not cols:
            cols = ('*',)
        if self._columns:
            return SelectQueryDataFrame(self._ctx, self).select(*cols)
        else:
            return copy_set(self, '_columns', *cols)
   
    def count(self):
        return self.select('count()')
 
    def first(self):
        return self.head(1)

    def head(self, rows=1):
        return copy_set(self, '_limit', rows)

    def limitBy(self, limit, by):
        return copy_set(self, '_limitby', limit, by)

    def vectorizeBy(self, key, sort, attributes=None):
        return copy_set(self, '_vectorizeby', key, attributes, sort)

    def join(self, jointype, right, keys=None, strictness=JoinStrictness.All, global_mode=False):
        return JoinDataFrame(self._ctx, jointype, self, right, keys, strictness, global_mode)

    def ej(self, right, keys, strictness=JoinStrictness.All, global_mode=False):
        return self.join(JoinType.Inner, right, keys, strictness, global_mode)

    def rj(self, left, keys, strictness=JoinStrictness.All, global_mode=False):
        return self.join(JoinType.Right, left, keys, strictness, global_mode)

    def lj(self, right, keys, strictness=JoinStrictness.All, global_mode=False):
        return self.join(JoinType.Left, right, keys, strictness, global_mode)

    def fj(self, right, keys, strictness=JoinStrictness.All, global_mode=False):
        return self.join(JoinType.Full, right, keys, strictness, global_mode)

    def aj(self, right, keys, global_mode=False):
        return self.join(JoinType.Join, right, keys, JoinStrictness.AsOf, global_mode)

    def cj(self, right, global_mode=False):
        return self.join(JoinType.Cross,
                         right,
                         keys=None,
                         strictness=JoinStrictness.Empty,
                         global_mode=global_mode)

    def _get_query(self):
        q = 'SELECT'
        if self._with_:
            q = 'WITH {} {}'.format(', '.join(map(str, self._with_)), q)
        if self._distinct:
            q = f'{q} DISTINCT'
        if self._columns:
            q = '{} {}'.format(q, ', '.join(map(str, self._columns)))
        if self._join:
            q = '{} FROM {}'.format(q, str(self._join))
        elif self._table:
            if isinstance(self._table[0], type(self)):
                q = '{} FROM ({})'.format(q, self._table[0]._get_query())
            else:
                q = '{} FROM {}'.format(q, ', '.join(map(str, self._table)))
        if self._where:
            q = '{} WHERE {}'.format(q, ' AND '.join(map(str, self._where)))
        if self._prewhere:
            q = '{} PREWHERE {}'.format(q, ' AND '.join(map(str, self._prewhere)))
        if self._vectorizeby:
            if self._vectorizeby[1]:
                q = '{} VECTORIZE BY ({}, {}, {})'.format(q, *self._vectorizeby)
            else:
                q = '{} VECTORIZE BY ({}, {})'.format(q, self._vectorizeby[0], self._vectorizeby[2])
        if self._groupby:
            q = '{} GROUP BY {}'.format(q, ', '.join(self._groupby))
            if self._having:
                q = '{} HAVING {}'.format(q, ', '.join(self._having))
        if self._orderby:
            q = '{} ORDER BY {}'.format(q, ', '.join(self._orderby))
        if self._limitby:
            q = '{} LIMIT {} BY {}'.format(q, self._limitby[0], ', '.join(self._limitby[1]))
        if self._limit:
            q = '{} LIMIT {}'.format(q, self._limit[0])
            if len(self._limit) == 2:
                q = '{} OFFSET {}'.format(q, self._limit[1])
        return q

    #def __repr__(self):
    #    return str(self.limit(self.max_rows).exec().show_pandas(self.max_preview_rows))


class UpdateQueryDataFrame(VulknDataFrame, ShowSQLMixin):
    def __init__(self, ctx, table):
        self._ctx = ctx
        self._table = table
        self._updates = None
        self._where = None
    
    def __getattr__(self, attrname):
        attrs = { 'set_': '_updates', 'where': None }
        if attrname in attrs.keys():
            attr = attrs[attrname] or '_{}'.format(attrname.lower())
            return partial(copy_set, self, attr)
        else:
            raise AttributeError

    def sync(self):
        self._sync = True
        return self

    def _get_query(self):
        where = ' AND '.join(self._where or ['1 = 1'])
        columns = ', '.join(self._updates)
        table = self._table
        return f'ALTER TABLE {table} UPDATE {columns} WHERE {where}'

    def exec(self):
        r = self._ctx.exec(self._get_query())
        d = self._ctx.table('system.mutations').select('*').where("database || '.' || table = '{}'".format(self._table)).exec()
        print(d)
        if not self._sync:
            return r
        print(r)
        


class DeleteQueryDataFrame(VulknDataFrame, ShowSQLMixin):
    def __init__(self, ctx, table):
        self._ctx = ctx
        self._table = table
        self._where = None

    def __getattr__(self, attrname):
        attrs = {'where': None}
        if attrname in attrs.keys():
            attr = attrs[attrname] or '_{}'.format(attrname.lower())
            return partial(copy_set, self, attr)
        else:
            raise AttributeError

    def _get_query(self):
        table = self._table
        if self._where is None:
            return f'TRUNCATE TABLE {table}'
        where = ' AND '.join(self._where)
        return f'ALTER TABLE {table} DELETE WHERE {where}'

    def sync(self):
        self._sync = True
        return self

    def exec(self):
        mutations = (self._ctx
                     .table('system.mutations')
                     .select('*')
                     .where("database || '.' || table = '{}'".format(self._table),
                            'is_done = 0',
                            "latest_fail_reason != ''",
                            "command LIKE 'DELETE%'")
                     .exec()
                     .to_records())
        if len(mutations) > 0:
            errors = [d['mutation_id'] + ': ' + d['latest_fail_reason'] for d in mutations]
            raise Exception('There are unfinished failed mutations for this table: \n' + '\n'.join(errors))
        r = self._ctx.exec(self._get_query())
        d = self._ctx.table('system.mutations').select('*').where("database || '.' || table = '{}'".format(self._table)).exec().to_records()
        if len(d[0]['latest_fail_reason']) > 0:
            raise Exception('Delete operation failed: ' + d[0]['latest_fail_reason'])
        if not self._sync:
            return r
        return r
