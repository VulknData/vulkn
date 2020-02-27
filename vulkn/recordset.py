# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import collections
import csv
import ast
import itertools
import logging
import ciso8601
import pandas as pd 
import numpy as np
import io
import datetime
import tabulate
from typing import List


from vulkn.utils import timer


log = logging.getLogger()
np.set_printoptions(suppress=True)
tabulate.PRESERVE_WHITESPACE = True


class TypeInfoMap:
    CONVERSION_MAP = {
        'UInt8': { 'native': lambda x: int(x), 'pandas': np.dtype('u1') },
        'UInt16': { 'native': lambda x: int(x), 'pandas': np.dtype('u2') },
        'UInt32': { 'native': lambda x: int(x), 'pandas': np.dtype('u4') },
        'UInt64': { 'native': lambda x: int(x), 'pandas': np.dtype('u8') },
        'Int8': { 'native': lambda x: int(x), 'pandas': np.dtype('i1') },
        'Int16': { 'native': lambda x: int(x), 'pandas': np.dtype('i2') },
        'Int32': { 'native': lambda x: int(x), 'pandas': np.dtype('i4') },
        'Int64': { 'native': lambda x: int(x), 'pandas': np.dtype('i8') },
        'Float32': { 'native': lambda x: float(x), 'pandas': np.dtype('f4') },
        'Float64': { 'native': lambda x: float(x), 'pandas': np.dtype('f8') },
        'Decimal': { 'native': lambda x: float(x), 'pandas': np.float },
        'DateTime': { 'native': lambda x: ciso8601.parse_datetime(x), 'pandas': np.dtype('M') },
        'Date': { 'native': lambda x: ciso8601.parse_datetime(x), 'pandas': np.dtype('M') }
    }

    NATIVE_CONVERSION_MAP = dict((k, v['native']) for k, v in CONVERSION_MAP.items())
    PANDAS_CONVERSION_MAP = dict((k, v['pandas']) for k, v in CONVERSION_MAP.items())

    @staticmethod
    def native_marshall_map(chtypes):
        types = []
        for t in chtypes:
            if t in TypeInfoMap.NATIVE_CONVERSION_MAP:
                types.append(TypeInfoMap.NATIVE_CONVERSION_MAP[t])
            else:
                if t.startswith('Array(') or t.startswith('Tuple('):
                    types.append(ast.literal_eval)
                else:
                    types.append(str)
        return types

    @staticmethod
    def pandas_marshall_map(columns, chtypes):
        # TODO: Fix type conversion of nested types or adopt Arrow/Parquet approach.
        types = {}
        for c, t in zip(columns, chtypes):
            if t in TypeInfoMap.PANDAS_CONVERSION_MAP:
                types[c] = TypeInfoMap.PANDAS_CONVERSION_MAP[t]
        return types


def ConsoleOutputFormatter(results: List[List[str]], columns: List[str]) -> str:
    return '\n{results}\n\n({rowcount} row{plural})\n'.format(
                                    results=tabulate.tabulate(results, columns, tablefmt='simple'),
                                    rowcount=len(results),
                                    plural='' if len(results) == 1 else 's')


class Row(collections.OrderedDict):
    def __init__(self, column_names, types, data):
        d = [(column_names[i], None if r == '\\N' else types[i](r)) for i, r in enumerate(data)]
        super(Row, self).__init__(d)


class RecordSet():
    def __init__(self, raw):
        # TODO: Raw is a cached version of the result as a string/blob that is re-interpreted 
        # each time. This makes no sense. Modify interface to use clickhouse-driver, Parquet -> Arrow
        # or another method under the hood.
        self._data = raw
        self._columns = None
        self._chtypes = None
        self._pytypes = None
        self._pdtypes = None
        self._marshall_info_ = None
        self._result = None

    @property
    def columns(self):
        if not self._columns:
            c = pd.read_csv(io.StringIO(self._data), sep='\t', header=None, na_values='\\N', nrows=1)
            self._columns = c.values.tolist()[0]
        return self._columns

    @property
    def chtypes(self):
        if not self._chtypes:
            c = pd.read_csv(io.StringIO(self._data),
                            skiprows=([0]),
                            sep='\t',
                            header=None,
                            na_values='\\N',
                            nrows=1)
            self._chtypes = c.values.tolist()[0]
        return self._chtypes

    @property
    def pytypes(self):
        # TODO: Unify with TypeMap
        if not self._pytypes:
            types = []
            for t in self.chtypes:
                if t.startswith('UInt') or t.startswith('Int'):
                    types.append(int)
                elif t.startswith('Float') or t.startswith('Decimal'): 
                    types.append(float)
                elif t == 'DateTime':
                    types.append(datetime.datetime)
                elif t == 'Date':
                    types.append(datetime.date)
                elif t.startswith('Array(') or t.startswith('Tuple('):
                    types.append(object)
                else:
                    types.append(str)
            self._pytypes = types
        return self._pytypes

    @property
    def pdtypes(self):
        if not self._pdtypes:
            self._pdtypes = TypeInfoMap.pandas_marshall_map(self.columns, self.chtypes)
        return self._pdtypes

    @property
    def _marshall_info(self):
        if not self._marshall_info_:
            self._marshall_info_ = TypeInfoMap.native_marshall_map(self.chtypes)
        return self._marshall_info_

    def to_pandas(self):
        if self._result is None:
            self._result = pd.read_csv(
                io.StringIO(self._data
                    .replace('\t\\N\t', '\t#NULL\t')
                    .replace('\\N\t', '#NULL\t')
                    .replace('\t\\N\n', '\t#NULL\n')
                    .replace('\\N\n', '#NULL\n')),
                skiprows=([1]),
                sep='\t',
                header=0,
                na_values='#NULL',
                parse_dates=True,
                engine='c',
                infer_datetime_format=True)
        return self._result

    def to_dict(self):
        return self.to_pandas().to_dict('record')

    def to_records(self):
        return self.to_pandas().to_dict('record')
 
    def to_list(self):
        return self.to_recarray().tolist()

    def to_recarray(self):        
        return self.to_pandas().to_records(index=False)

    def show(self):        
        table = self.to_pandas().values[0:1000].tolist()
        table = [[i+1]+r for i, r in enumerate(table)]
        print(ConsoleOutputFormatter(table, ['row'] + self.columns))

    def show_pandas(self, num_rows=50):
        pd.options.display.max_rows = num_rows
        return self.to_pandas()

    s = property(show)
    r = property(to_records)
    p = property(to_pandas)
    d = property(to_dict)
    l = property(to_list)
    n = property(to_recarray)

    def __len__(self):
        return len(self.to_pandas())

    def __getitem__(self, key):
        cnt = itertools.count(1)
        if isinstance(key, slice):
            for row in csv.reader(self._data[key.start + 2:key.stop], delimiter='\t', quotechar='"'):
                c = next(cnt)
                if(c%100000 == 0):
                    log.debug(f"Read {c} records...")
                yield Row(self.columns, self._marshal_info, row)
            c = next(cnt)
            log.debug(f"Read {c} records...")
        elif isinstance(key, int):
            for row in csv.reader([self._data[key + 2]], delimiter='\t', quotechar='"'):
                yield Row(self.columns, self._marshal_info, row)

