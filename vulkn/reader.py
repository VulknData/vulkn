# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import csv
import os
import ast
import re


import vulkn
from vulkn.clickhouse import sqlformat
from vulkn.formats.csv import CSV
from vulkn.storages.posix import PosixStorage
from vulkn.datatable import BaseTableDataTable
from vulkn.utils import timer


class Reader:
    def __init__(self):
        pass

    def format(self, format):
        # TODO: Next release. Auto-discover/load formats
        if format == 'csv':
            return DataManager(CSV())


class DataManager:
    def __init__(self, format):
        self._format = format

    def options(self, **kwargs):
        self._format = self._format.options(**kwargs)
        return self

    @timer
    def load(self, uri, database, table):
        # TODO: Next release. Use proper vulkn method
        def _create_table(database, table, columns, engine):
            ctx = vulkn.Vulkn()
            column_ddl = ', '.join(['"{}" {}'.format(k, v) for k, v in columns.items()])
            create_ddl = f'CREATE TABLE "{database}"."{table}" ({column_ddl}) ENGINE = {engine}'
            if not ctx.exec(create_ddl):
                raise Exception('Unable to create table')

        schema = self._format._options['schema']
        tmp_db = database
        ctx = vulkn.Vulkn()

        if schema:
            cols = [c._name for c in schema]
            types = [c._col_type for c in schema]

        if schema is None or self._format._options['infer_schema']:
            cols = self._format.columns(PosixStorage(uri))
            types = ['String']*len(cols)
            if self._format._options['column_format'] == 'snake_case':
                cols = [snake_case(c) for c in cols]
            sample_engine = self._format._options['sample_engine'] or vulkn.engines.Memory()
            ctx.dropTable(tmp_db, f'tmp_{table}')
            _create_table(tmp_db, f'tmp_{table}', dict(zip(cols, types)), sample_engine)
            # TODO: Next release. Use storage.write method
            sample = self._format.sample(PosixStorage(uri))
            ctx._conn.insert_blob(sample, tmp_db + f'."tmp_{table}"', 'CSV')
            types = infer_column_types(tmp_db,
                                       f'tmp_{table}',
                                       cols,
                                       self._format._options['sample_size'],
                                       self._format._options['allow_enums'])
            ctx.dropTable(tmp_db, f'tmp_{table}')

        if self._format._options['overwrite']:
            ctx.dropTable(database, table)

        _create_table(database,
                      table,
                      dict(zip(cols, types)), 
                      engine=self._format._options['engine'] or vulkn.engines.Memory())

        if self._format._options['infer_schema']:
            sample_engine = self._format._options['sample_engine'] or vulkn.engines.Memory()
            _create_table(tmp_db, f'tmp_{table}', dict(zip(cols, types)), sample_engine)
            # TODO: Next release. Write without cat
            self._format.read(PosixStorage(uri), tmp_db, f'tmp_{table}')
            convert_dml = marshal_columns(tmp_db, f'tmp_{table}', database, table, cols, types)
            if ctx._conn.execute(convert_dml) != 0:
                raise Exception('Unable to load data')
            ctx.dropTable(tmp_db, f'tmp_{table}')
        else:
            # TODO: Next release. Write without cat
            self._format.read(PosixStorage(uri), database, table)

        return BaseTableDataTable(ctx, database, table).select('*')
        

def snake_case(name):
    f = ['#','/','<','(',')','%','|','@','.','-',' ','[',']','!','%','+','__']
    r = ['num','_','lt','','','','','','_','_','_','_','_','','pct','_','_']
    s = name.replace('dB', 'db').replace('MHz', 'mhz').replace('Mbit/s', 'mbps')
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    for fs, rs in dict(zip(f,r)).items():
        s = s.replace(fs, rs)
    return s.lower()
    

def infer_column_types(database, table, columns, sample=0, allow_enums=True):
    tests = []
    results = []
    ctx = vulkn.Vulkn()
    for col in columns:
        r = ctx._conn.select(infer_column_type(database, table, col, sample)).to_records()
        if len(r) > 0:
            tests.append(r[0])
    for i, col in enumerate(tests):
        r = ''
        if tests[i]['recommended_type'] == 'String' and tests[i]['enum'] and allow_enums:
            enum = ["'{}'={}".format(st, str(idx+1))
                for idx, st in enumerate(sorted(ast.literal_eval(tests[i]['sample'])))]
            r = "Enum({})".format(', '.join(enum))
        else:
            r = tests[i]['recommended_type']
        if tests[i]['nullable']:
            r = 'Nullable({})'.format(r)
        if tests[i]['low_cardinality']:
            r = 'LowCardinality({})'.format(r)
        results.append(r)
    return results


def marshal_columns(src_database, src_table, target_database, target_table, columns, types):
    cols = []
    for i, t in enumerate(types):
        c = 'nullIf(trim(toString("{}")), \'\')'.format(columns[i])
        if t in ('DateTime', 'Date'):
            c = 'parseDateTimeBestEffortOrNull({})'.format(c)
        cols.append(c)
    columns = ','.join(cols)
    database = target_database
    table = target_table
    sql = f'INSERT INTO {database}.{table} SELECT {columns} FROM {src_database}.{src_table}'
    return sqlformat(sql)


def infer_column_type(database, table, column, sample=0):
    sample = 0
    sql = """
        SELECT
            '{column}' AS col_name,
            any(nullable) AS nullable,
            (uniq_approx < 6 AND recommended_type = 'String') AS enum,
            (uniq_approx > 10 AND uniq_approx < 1000000 AND recommended_type = 'String') AS low_cardinality,
            recommended_type,
            any(sample) AS sample,
            any(uniq_approx) AS uniq_approx
        FROM (
            SELECT
                (null_cnt > 0) AS nullable,
                multiIf(
                    uint_cnt = non_null_cnt,
                        multiIf(
                            length(toString(toUInt8OrNull(col))) = length(col), 'UInt8',
                            length(toString(toUInt16OrNull(col))) = length(col), 'UInt16',
                            length(toString(toUInt32OrNull(col))) = length(col), 'UInt32',
                            length(toString(toUInt64OrNull(col))) = length(col), 'UInt64',
                            'String'),
                    int_cnt = non_null_cnt,
                        multiIf(
                            length(toString(toInt8OrNull(col))) = length(col), 'Int8',
                            length(toString(toInt16OrNull(col))) = length(col), 'Int16',
                            length(toString(toInt32OrNull(col))) = length(col), 'Int32',
                            length(toString(toInt64OrNull(col))) = length(col), 'Int64',
                            'String'),
                    float_cnt = non_null_cnt,
                        multiIf(
                            length(toString(toFloat32OrNull(col))) = length(col), 'Float32',
                            length(toString(toFloat64OrNull(col))) = length(col), 'Float64',
                            'String'),
                    datetime_cnt = non_null_cnt,
                        if(parseDateTimeBestEffortOrNull(col) IS NOT NULL, 'DateTime', 'String'),
                    date_cnt = non_null_cnt,
                        if(parseDateTimeBestEffortOrNull(col) IS NOT NULL, 'Date', 'String'),
                    'String') AS recommended_type,
                sample,
                if({sample} == 0, any(uniq_values), any(toUInt64(uniq_values*(100/{sample})))) AS uniq_approx
            FROM (
                SELECT
                    '{column}' AS col_name,
                    toString("{column}") AS col
                FROM {database}.{table_name}
                WHERE if({sample} == 0, 1, rand(1)%100 <= ({sample} - 1))
            ) ALL INNER JOIN (
                SELECT
                    col_name,
                    count() AS col_cnt,
                    countIf(col IS NULL) AS null_cnt,
                    col_cnt - null_cnt AS non_null_cnt,
                    sum(match(col, '^([\-0-9\.]*)$')) AS float_cnt,
                    sum(match(col, '^([\-0-9]*)$')) AS int_cnt,
                    sum(match(col, '^([0-9]*)$')) AS uint_cnt,
                    sum(match(col, '.*([0-9]{{2}}:[0-9]{{2}}).*')) AS datetime_cnt,
                    sum(match(col, '.*([0-9]{{2}}[/\-][0-9]{{2}}[/\-][0-9]{{2}}).*')) AS date_cnt,
                    uniqExact(col) AS uniq_values,
                    topK(10)(col) AS sample
                FROM (
                    SELECT
                        '{column}' AS col_name,
                        nullIf(trim(toString("{column}")), '') AS col
                    FROM {database}.{table_name}
                    WHERE if({sample} == 0, 1, rand(1)%100 <= ({sample} - 1))
                ) GROUP BY col_name
            ) USING (col_name)
            GROUP BY nullable, recommended_type, sample
        ) GROUP BY recommended_type, col_name
        ORDER BY
            recommended_type = 'UInt64' DESC
            , recommended_type = 'UInt32' DESC
            , recommended_type = 'UInt16' DESC
            , recommended_type = 'UInt8' DESC
            , recommended_type = 'Int64' DESC
            , recommended_type = 'Int32' DESC
            , recommended_type = 'Int16' DESC
            , recommended_type = 'Int8' DESC
            , recommended_type = 'Float64' DESC
            , recommended_type = 'Float32' DESC
            , recommended_type = 'DateTime' DESC
            , recommended_type = 'Date' DESC
            , recommended_type = 'String' DESC
        LIMIT 1
    """
    return sqlformat(sql.format(database=database, column=column, table_name=table, sample=sample))
