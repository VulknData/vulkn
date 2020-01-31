# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import copy
import logging
import random
import sys
from functools import partial


import vulkn.session
from vulkn.clickhouse import sqlformat
from vulkn.utils import VulknSQLFormatter, timer, LogLevels


log = logging.getLogger()


# TODO: Next release. Add table function datatables:
# https://clickhouse.yandex/docs/en/query_language/table_functions/


def copy_set(obj, key, *value):
    bool_keys = ['_distinct']
    this = copy.deepcopy(obj)
    if key in bool_keys:
        setattr(this, key, True)
    else:
        setattr(this, key, value)
    if key in this._op_chain:
        raise Exception(f'Operation {key} already set')
    else:
        this._op_chain.append(key)
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


class VulknDataTable:   
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


def JoinDataTable(
        ctx, jointype, left, right, keys=None, strictness=JoinStrictness.All, global_mode=False):
    j = '({left}) {left_alias}{global_mode} {strictness} {join_type} JOIN ({right}) {right_alias}'
    left_alias = ''
    right_alias = ''
    if hasattr(left, '_alias') and left._alias is not None:
        left_alias = f'AS "{left._alias[0]}"'
    if hasattr(right, '_alias') and right._alias is not None:
        right_alias = f'AS "{right._alias[0]}"'
    q = j.format(left=left._get_query(), 
                 left_alias=left_alias,
                 global_mode='GLOBAL' if global_mode else '',
                 strictness=strictness,
                 join_type=jointype,
                 right=right._get_query(),
                 right_alias=right_alias)
    left_cols = [f'{l._name} AS "{left._alias[0]}.{l._name}"' 
        if left_alias else l for l in left.get_schema()]
    right_cols = [f'{r._name} AS "{right._alias[0]}.{r._name}"'
        if right_alias else r for r in right.get_schema()]
    if keys:
        q = '{} USING ({})'.format(q, ','.join(keys))
    return SelectQueryDataTable(ctx, q).select(*[*left_cols, *right_cols])


def NumbersDataTable(ctx, count, system=False, mt=False):
    if system:
        t = 'system.numbers' + ('_mt' if mt else '')
        return SelectQueryDataTable(ctx, t).limit(count).select('*')
    else:
        t = 'numbers' + ('_mt' if mt else '')
        return SelectQueryDataTable(ctx, '{}({})'.format(t, count)).select('*')


def RandomDataTable(ctx, count, start=0, end=((sys.maxsize*2)+1), system=False, mt=False):
    q = f'{start} + rand()%(if(mod == 0, mod - 1, ({end}-({start})+1) AS mod)) AS number'
    if system:
        t = 'system.numbers' + ('_mt' if mt else '')
        return SelectQueryDataTable(ctx, t).limit(count).select(q)
    else:
        t = 'numbers' + ('_mt' if mt else '')
        return SelectQueryDataTable(ctx, '{}({})'.format(t, count)).select(q)


def RandomFloatDataTable(ctx, count, start=0, end=((sys.maxsize*2)+1), system=False, mt=False):
    maxsize = ((sys.maxsize*2)+1)
    q = f"{start} + rand64()%({end}-({start})) + rand64()/{maxsize} AS number"
    if system:
        t = 'system.numbers' + ('_mt' if mt else '')
        return SelectQueryDataTable(ctx, t).limit(count).select(q)
    else:
        t = 'numbers' + ('_mt' if mt else '')
        return SelectQueryDataTable(ctx, '{}({})'.format(t, count)).select(q)


def OneDataTable(ctx):
    return SelectQueryDataTable(ctx, 'system.one').select('*')


def RangeDataTable(ctx, start, end, system=False, mt=False):
    if end <= start:
        raise Exception('end must be greater than start')
    if system or mt:
        t = 'system.numbers' + ('_mt' if mt else '')
        return (SelectQueryDataTable(ctx, t)
                .limit(end + 1 -(start))
                .select('number + {} AS range'.format(str(start))))
    else:
        return (SelectQueryDataTable(ctx, 'numbers({})'.format(end + 1 -(start)))
                .select('number + {} AS range'.format(str(start))))


def aj(datatables, keys, global_mode=False):
    df = datatables[0]
    for d in datatables:
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
        return SelectQueryDataTable(self._ctx, t).select('*')


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
        return SelectQueryDataTable(self._ctx, f'{database}.{table}').select('*')


class QueryExecutorMixin:
    def plan(self, **params):
        q = self._get_query()
        statements = vulkn.sql.SQLMessage(VulknSQLFormatter().format(q, **params)).statements()
        if len(statements) > 1:
            raise Exception('More than one statement is not supported')
        return QueryStringDataTable(self._ctx, statements[0].optimize()).select('*')

    @timer
    def exec(self, **params):
        q = self._get_query()
        statements = vulkn.sql.SQLMessage(VulknSQLFormatter().format(q, **params)).statements()
        if len(statements) > 1:
            raise Exception('More than one statement is not supported')
        return self._ctx._conn.select(statements[0].optimize())

    def get_schema(self):
        name = f'v{random.randint(1,sys.maxsize)}'
        c = None
        try:
            self._ctx.drop_view('vulkn', name)
            self._ctx.create_view('vulkn', name, self.show_sql()[0:-1])
            c = self._ctx.get_schema('vulkn', name)
        finally:
            self._ctx.drop_view('vulkn', name)
        return c

    def to_records(self):
        return self.exec().to_records()

    def to_pandas(self):
        return self.exec().to_pandas()

    def show(self):
        return self.exec().show()

    def to_list(self):
        return self.exec().to_list()

    def to_dict(self):
        return self.exec().to_dict()

    def to_recarray(self):
        return self.exec().to_recarray()

    r = property(to_records)
    s = property(show)
    p = property(to_pandas)
    l = property(to_list)
    d = property(to_dict)
    n = property(to_recarray)
    e = exec


class BaseTableDataTable:
    def __init__(self, ctx, database, table):
        self._ctx = ctx
        self._database = database
        self._table = table

    def __str__(self):
        return '"{database}"."{table}"'.format(database=self._database, table=self._table)

    def __getattr__(self, attrname):
        return getattr(SelectQueryDataTable(self._ctx, str(self)), attrname)

    def desc(self):
        return self._ctx.q(f'DESC {self._database}.{self._table}').exec()

    def drop_columns(self, *columns):
        return self._ctx.drop_columns(self._database, self._table, columns)

    def load(self, parts=None):
        from vulkn.types import c
        dt = SelectQueryDataTable(self._ctx, str(self)).all()
        if parts:
            dt = dt.where(c('_part').in_(parts))
        q = dt._get_query()
        sql = VulknSQLFormatter().format(q, **self._params[0]) if self._params else q
        statements = vulkn.sql.SQLMessage(sql).statements()
        if len(statements) > 1:
            raise Exception('More than one statement is not supported')
        t = self._ctx.session.cache(statements[0].optimize(), engine=vulkn.engines.Memory())
        return BaseTableDataTable(self._ctx, *(t.split('.')))


class QueryStringDataTable(VulknDataTable, QueryExecutorMixin, ShowSQLMixin, CachedQueryMixin, TableWriterMixin):
    def __init__(self, ctx, query):
        self._ctx = ctx
        self._query = query

    def _get_query(self):
        return self._query

    def __getattr__(self, attrname):
        attrs = ['limit','where','filter','limit_by','limitBy','head','first','distinct',
            'order_by','orderBy','sort','prewhere','preWhere']
        this = SelectQueryDataTable(self._ctx, '({})'.format(self._get_query()))
        if attrname.lower() in attrs:
            return getattr(this.select('*'), attrname)
        else:
            return getattr(this, attrname)


class SelectQueryDataTable(VulknDataTable,
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
        self._group_by = None
        self._group_by_with_totals = False
        self._order_by = None
        self._having = None
        self._limit = None
        self._limit_by = None
        self._vectorize_by = None
        self._join = None
        self._with_ = None
        self._params = None
        self._array_join = None
        self._left_array_join = None
        self._alias = None
        self._op_chain = []

    def __getattr__(self, attrname):
        attrs = {
            'alias': None,
            'as_': '_alias',
            'with_': None,
            'distinct': None,
            'from_': '_table',
            'prewhere': None,
            'preWhere': '_prewhere',
            'where': None,
            'filter': '_where',
            'order_by': None,
            'orderBy': '_order_by',
            'sort': '_order_by',
            'having': None,
            'limit': None,
            'params': None,
            'array_join': None,
            'arrayJoin': '_array_join',
            'left_array_join': None,
            'leftArrayJoin': '_left_array_join'
        }

        if attrname in attrs.keys():
            attr = attrs[attrname] or '_{}'.format(attrname.lower())
            dt = self._subquery() if getattr(self, attr) is not None else self
            return partial(copy_set, dt, attr)
        else:
            raise AttributeError

    def _subquery(self):
        return SelectQueryDataTable(self._ctx, self)

    def all(self):
        cols = ('*',)
        if not isinstance(self._table[0], type(self)):
            try:
                table = self._table[0].rsplit('.')[1].strip('"')
                cols = [t._name for t in self._ctx.getSchema(table)]
            except:
                cols = ('*',)
        return self.select(*cols)

    def select(self, *cols):
        if not cols:
            cols = ('*',)
        if self._columns:
            return self._subquery().select(*cols)
        else:
            return copy_set(self, '_columns', *cols)
   
    def count(self):
        return self._subquery().select('count()')
 
    def first(self):
        return self.head(1)

    def head(self, rows=1):
        return copy_set(self, '_limit', rows)

    def limit_by(self, limit, by):
        dt = self._subquery() if self._limit_by else self
        return copy_set(dt, '_limit_by', limit, by)

    limitBy = limit_by

    def group_by(self, *cols, with_totals=False):
        r = None
        if self._group_by:
            r = self._subquery().group_by(*cols)
        else:
            r = copy_set(self, '_group_by', *cols)
        r._group_by_with_totals = with_totals
        return r

    groupBy = group_by

    def vectorize_by(self, key, sort, attributes=None):
        if self._vectorize_by or self._group_by or self._order_by:
            return self._subquery().all().vectorize_by(key, sort, attributes)
        else:
            return copy_set(self, '_vectorize_by', key, attributes, sort)

    vectorizeBy = vectorize_by

    def join(self, jointype, right, keys=None, strictness=JoinStrictness.All, global_mode=False):
        return JoinDataTable(self._ctx, jointype, self, right, keys, strictness, global_mode)

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
                         strictness=JoinStrictness.Default,
                         global_mode=global_mode)

    def _get_query(self):
        q = 'SELECT'
        if self._with_:
            q = 'WITH {} {}'.format(', '.join(map(str, self._with_)), q)
        if self._distinct:
            q = f'{q} DISTINCT'
        if self._columns:
            q = '{} {}'.format(q, ', '.join(map(str, self._columns)))
        else:
            q = f'{q} *'
        if self._join:
            q = '{} FROM {}'.format(q, str(self._join))
        elif self._table:
            if isinstance(self._table[0], type(self)):
                q = '{} FROM ({})'.format(q, self._table[0]._get_query())
                if hasattr(self._table[0], '_alias') and self._table[0]._alias is not None:
                    q = '{} AS "{}"'.format(q, self._table[0]._alias[0])
            else:
                q = '{} FROM {}'.format(q, ', '.join(map(str, self._table)))
        if self._array_join or self._left_array_join:
            if self._array_join:
                q = '{} ARRAY JOIN {}'.format(q, ', '.join(map(str, self._array_join)))
            else:
                q = '{} LEFT ARRAY JOIN {}'.format(q, ', '.join(map(str, self._left_array_join)))
        if self._where:
            q = '{} WHERE {}'.format(q, ' AND '.join(map(str, self._where)))
        if self._prewhere:
            q = '{} PREWHERE {}'.format(q, ' AND '.join(map(str, self._prewhere)))
        if self._vectorize_by:
            if self._vectorize_by[1]:
                q = '{} VECTORIZE BY ({}, {}, {})'.format(q, *self._vectorize_by)
            else:
                q = '{} VECTORIZE BY ({}, {})'.format(q,
                                                      self._vectorize_by[0],
                                                      self._vectorize_by[2])
        if self._group_by:
            q = '{} GROUP BY {}'.format(q, ', '.join(map(str, self._group_by)))
            if self._group_by_with_totals:
                q = f'{q} WITH TOTALS'
            if self._having:
                q = '{} HAVING {}'.format(q, ', '.join(map(str, self._having)))
        if self._order_by:
            q = '{} ORDER BY {}'.format(q, ', '.join(map(str, self._order_by)))
        if self._limit_by:
            q = '{} LIMIT {} BY {}'.format(q, 
                                           str(self._limit_by[0]),
                                           ', '.join(map(str, self._limit_by[1])))
        if self._limit:
            q = '{} LIMIT {}'.format(q, str(self._limit[0]))
            if len(self._limit) == 2:
                q = '{} OFFSET {}'.format(q, str(self._limit[1]))
        return q

    #def __repr__(self):
    #    return str(self.limit(self.max_rows).exec().show_pandas(self.max_preview_rows))


class UpdateQueryDataTable(VulknDataTable, ShowSQLMixin):
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
        


class DeleteQueryDataTable(VulknDataTable, ShowSQLMixin):
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
