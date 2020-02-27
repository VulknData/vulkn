# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import copy
import logging
import random
import sys
import pandas as pd
from collections import namedtuple
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
    if key is None:
        return this
    elif key in bool_keys:
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
    Semi='SEMI'
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


class JoinGroupDataTable(VulknDataTable):
    def __init__(self, ctx, dt):
        self._ctx = ctx
        self._tables = [dt]

    def append(self, jointype, other, keys=None, strictness=JoinStrictness.All, global_mode=False, using=False):
        self._tables.append((jointype, other, keys, strictness, global_mode, using,))

    def __str__(self):
        r = ''
        if (isinstance(self._tables[0], SelectQueryDataTable)
                or isinstance(self._tables[0], QueryStringDataTable)):
            r = f'({self._tables[0]._get_query()})'
            alias = getattr(self._tables[0], '_alias', None)
            if alias:
                r = r + f' AS "{alias[0]}"'
        else:
            r = str(self._tables[0])
        for t in self._tables[1:]:
            global_mode = 'GLOBAL ' if t[4] else ''
            table = ''
            if (isinstance(t[1], SelectQueryDataTable) or isinstance(t[1], QueryStringDataTable)):
                table = f'({t[1]._get_query()})'
                alias = getattr(t[1], '_alias', None)
                if alias:
                    table = table + f' AS "{alias[0]}"'
            else:
                table = str(t[1])
            r = r + f' {t[3]} {t[0]} JOIN {table}'
            if t[2]:
                if t[5]:
                    r = r + ' USING (' + ', '.join(map(str, t[2])) + ')'
                else:
                    r = r + ' ON (' + ') AND ('.join(map(str, t[2])) + ')'
        return r


def aj(datatables, keys, global_mode=False):
    dt = datatables[0].aj(datatables[1], keys, global_mode=global_mode, using=True)
    for i, d in enumerate(datatables[2:]):
        dt = dt.alias(f'_{i}').aj(d, keys, global_mode=global_mode, using=True)
    return dt


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


class ShowSQLMixin:
    def _show_sql(self, **params):
        q = self._get_query()
        sql = VulknSQLFormatter().format(q, **params) if params else q
        return sql
 
    def show_sql(self, pretty_print=False, **params):
        q = self._get_query()
        sql = VulknSQLFormatter().format(q, **params) if params else q
        statements = vulkn.sql.SQLMessage(sql).statements()
        if len(statements) > 1:
            raise Exception('More than one statement is not supported')
        return sqlformat(statements[0].optimize(), oneline=not pretty_print)


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
        return BaseTableDataTable(self._ctx, *(t.split('.')))


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


class BaseTableDataTable(VulknDataTable):
    def __init__(self, ctx, database, table):
        self._ctx = ctx
        self._database = database
        self._table = table
        self._alias = None

    def __str__(self):
        r = f'"{self._database}"."{self._table}"'
        if self._alias:
            r = r + f' AS "{self._alias}"'
        return r

    def __getattr__(self, attrname):
        attrs = ['alias']
        if attrname.lower() not in attrs:
            return getattr(SelectQueryDataTable(self._ctx, self), attrname)
        else:
            raise AttributeError    

    def alias(self, alias_):
        self._alias = alias_
        return self

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

    def alias(self, alias_):
        this = SelectQueryDataTable(self._ctx, '({})'.format(self._get_query()))
        this._alias = (alias_,)
        return this

    as_ = alias


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
        self._with_ = None
        self._params = None
        self._array_join = None
        self._left_array_join = None
        self._alias = None
        self._op_chain = []

    def __getattr__(self, attrname):
        attrs = {
            'with_': None,
            'distinct': None,
            'from_': '_table',
            'prewhere': None,
            'preWhere': '_prewhere',
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

    def alias(self, alias_):
        r = self._subquery()
        r._table[0]._alias = (alias_,)
        return r

    as_ = alias

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

    def where(self, *cols):
        r = None
        if self._group_by:
            r = self._subquery().where(*cols)
        else:
            if self._where:
                r = copy_set(self, None, None)
                r._where = tuple(list(r._where) + list(cols))
            else:
                r = copy_set(self, '_where', *cols)
        return r

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

    def join(self, jointype, other, keys=None, strictness=JoinStrictness.All, global_mode=False, using=False):
        this = copy_set(self, None, None)
        if this._table:
            if not isinstance(this._table[0], JoinGroupDataTable):
                if isinstance(self._table[0], str):
                    table = QueryStringDataTable(self._ctx, self._table[0])
                    table._alias = this._alias
                    this._table = (JoinGroupDataTable(this._ctx, table),)
                else:
                    this._table = (JoinGroupDataTable(this._ctx, self._table[0]),)
            if isinstance(other, SelectQueryDataTable):
                other_table = None
                if isinstance(other._table[0], str):
                    other_table = QueryStringDataTable(other._ctx, other._table[0])
                    other_table._alias = other._alias
                else:
                    other_table = other
                this._table[0].append(jointype, other_table, keys, strictness, global_mode, using)
            else:
                this._table[0].append(jointype, other, keys, strictness, global_mode, using)
        else:
            raise Exception('No left table set')
        return this

    def ej(self, right, keys, strictness=JoinStrictness.All, global_mode=False, using=False):
        return self.join(JoinType.Inner, right, keys, strictness, global_mode, using)

    def rj(self, left, keys, strictness=JoinStrictness.All, global_mode=False, using=False):
        return self.join(JoinType.Right, left, keys, strictness, global_mode, using)

    def lj(self, right, keys, strictness=JoinStrictness.All, global_mode=False, using=False):
        return self.join(JoinType.Left, right, keys, strictness, global_mode, using)

    def fj(self, right, keys, strictness=JoinStrictness.All, global_mode=False, using=False):
        return self.join(JoinType.Full, right, keys, strictness, global_mode, using)

    def aj(self, right, keys, global_mode=False, using=False):
        return self.join(JoinType.Join, right, keys, JoinStrictness.AsOf, global_mode, using)

    def cj(self, right, global_mode=False, using=False):
        return self.join(JoinType.Cross,
                         right,
                         keys=None,
                         strictness=JoinStrictness.Default,
                         global_mode=global_mode,
                         using=using)

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
        if self._table:
            if isinstance(self._table[0], type(self)):
                q = '{} FROM ({})'.format(q, self._table[0]._get_query())
                if hasattr(self._table, '_alias') and self._table[0]._alias is not None:
                    q = '{} AS "{}"'.format(q, self._table[0]._alias[0])
            else:
                q = '{} FROM {}'.format(q, str(self._table[0]))
        if self._array_join or self._left_array_join:
            if self._array_join:
                q = '{} ARRAY JOIN {}'.format(q, ', '.join(map(str, self._array_join)))
            else:
                q = '{} LEFT ARRAY JOIN {}'.format(q, ', '.join(map(str, self._left_array_join)))
        if self._prewhere:
            q = '{} PREWHERE {}'.format(q, ' AND '.join(map(str, self._prewhere)))
        if self._where:
            q = '{} WHERE {}'.format(q, ' AND '.join(map(str, self._where)))
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
        if not self._sync:
            return r


class DeleteQueryDataTable(VulknDataTable, ShowSQLMixin):
    def __init__(self, ctx, table):
        self._ctx = ctx
        self._table = table
        self._where = None
        self._sync = False
        self._op_chain = []

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
                     .select('mutation_id', 'latest_fail_reason')
                     .where("database || '.' || table = '{}'".format(self._table),
                            'is_done = 0',
                            "latest_fail_reason != ''",
                            "command LIKE 'DELETE%'")
                     .exec()
                     .to_records())
        settings = {'mutations_sync': 1} if self._sync else None
        if len(mutations) > 0:
            errors = [d['mutation_id'] + ': ' + d['latest_fail_reason'] for d in mutations]
            raise Exception('There are unfinished failed mutations for this table: \n' + '\n'.join(errors))
        r = self._ctx._conn.execute(self._get_query(), settings=settings)
        d = (self._ctx
             .table('system.mutations')
             .select('*')
             .where("database || '.' || table = '{}'".format(self._table))
             .exec().to_records())
        latest_fail_reason = '' if pd.np.isnan(d[0]['latest_fail_reason']) else str(d[0]['latest_fail_reason'])
        if len(latest_fail_reason) > 0:
            raise Exception('Delete operation failed: ' + d[0]['latest_fail_reason'])
        if not self._sync:
            return r
        return r
