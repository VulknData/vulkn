# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import string
import socket
from timeit import default_timer
from functools import wraps


class LogLevels:
    SQL = 11


def get_next_free_socket(host, ports):
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        sock.close()
        if result != 0:
            return port
    return 0


def timer(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        import vulkn.session
        if vulkn.session.timing:
            start = default_timer()
        r = f(*args, **kwargs)
        if vulkn.session.timing:
            print('Time elapsed: {:0.3f} ms'.format(abs(default_timer() - start)*1000))
        return r
    return wrap


def item_index(index):
    start = 1
    stop = None
    if isinstance(index, slice):
        stop = 1 if index.stop == 0 else index.stop
        start = index.start
    else:
        start = index
    return (start, stop)


def column_list(columns):
    from vulkn.types import ArrayVector, ColumnVector
    rangeCols = []
    selectExprList = []
    for idx, column in enumerate(columns):
        if isinstance(column, ArrayVector):
            rangeCols.append(str(column))
        if isinstance(column, ColumnVector):
            if hasattr(column, 'vector_name'):
                selectExprList.append('c{index}.v AS {name}'.format(index=str(idx),
                                                                    name=column.vector_name))
            else:    
                selectExprList.append('c{index}.v AS col{index}'.format(index=str(idx)))
            subquery = 'SELECT i, v FROM {column}'.format(str(column))
            if idx == 0:
                rangeCols.append('FROM ({}) c0'.format(subquery))
            else:
                rangeCols.append(
                    'INNER JOIN ({subquery}) c{index} ON (c{prevIndex}.i = c{index}.i)'.format(
                        subquery=subquery, index=str(idx), prevIndex=str(i-1)))
    q = "SELECT {selectExpr} {rangeCols}".format(selectExpr=', '.join(selectExprList), 
                                                 rangeCols=' '.join(rangeCols))
    return q


class singleton:
    def __init__(self, cls):
        self.cls = cls
        self.instance = None
    
    def __call__(self, *args, **kwargs):
        if self.instance == None:
            self.instance = self.cls(*args, **kwargs)
        return self.instance


class VulknSQLFormatter(string.Formatter):
    # TODO: Next release. Unify with RecordSet conversion map
    CONVERSION_MAP = {
        'String': lambda x: "'{}'".format(str(x).encode('unicode-escape').decode()),
        'UInt8': lambda x: int(x),
        'UInt16': lambda x: int(x),
        'UInt32': lambda x: int(x),
        'UInt64': lambda x: int(x),
        'Int8': lambda x: int(x),
        'Int16': lambda x: int(x),
        'Int32': lambda x: int(x),
        'Int64': lambda x: int(x),
        'Float32': lambda x: float(x),
        'Float64': lambda x: float(x),        
        'DateTime': lambda x: "'{}'".format(str(x).encode('unicode-escape').decode()),
        'Date': lambda x: "'{}'".format(str(x).encode('unicode-escape').decode())
    }

    def format_field(self, value, format_spec):
        if format_spec in self.CONVERSION_MAP:
            return '{}'.format(self.CONVERSION_MAP[format_spec](value))
        else:
            return super().format_field(value, format_spec)
