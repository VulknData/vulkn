# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import sys
import random


from vulkn.sql.utils import ast_protect_injection


@ast_protect_injection
def vectorRowNumber():
    varg = random.randint(1,sys.maxsize)
    select_expr = f'v{varg}'
    arr_join_expr = (f'arrayEnumerate(`--#v`.1) AS v{varg}',)
    return (select_expr, arr_join_expr)

vectorRowNum = vectorRowNumber

@ast_protect_injection
def vectorAgg(agg, v):
    varg = random.randint(1,sys.maxsize)
    select_expr = f'v{varg}'
    arr_join_expr = (f"arrayWithConstant(length(__{v}), arrayReduce('{agg}', __{v})) AS v{varg}",)
    return (select_expr, arr_join_expr)

@ast_protect_injection
def vectorFirst(v):
    varg = random.randint(1,sys.maxsize)
    select_expr = f'v{varg}'
    arr_join_expr = (f"arrayWithConstant(length(__{v}), (__{v})[1]) AS v{varg}",)
    return (select_expr, arr_join_expr)

@ast_protect_injection
def vectorLast(v):
    varg = random.randint(1,sys.maxsize)
    select_expr = f'v{varg}'
    arr_join_expr = (f"arrayWithConstant(length(__{v}), (__{v})[-1]) AS v{varg}",)
    return (select_expr, arr_join_expr)

@ast_protect_injection
def vectorLag(v, offset=-1):
    offset = int(str(offset))
    if offset > -1:
        raise Exception('Parameter "offset" must be less than 0')
    varg = random.randint(1,sys.maxsize)
    select_expr = f'v{varg}'
    arr_join_expr = (f"arrayConcat(arrayWithConstant(abs({offset}), NULL), arraySlice(__{v}, 1, {offset})) AS v{varg}",)
    return (select_expr, arr_join_expr)

@ast_protect_injection
def vectorLead(v, offset=1):
    offset = int(str(offset))
    if offset < 1:
        raise Exception('Parameter "offset" must be greater than 0')
    varg = random.randint(1,sys.maxsize)
    select_expr = f'v{varg}'
    arr_join_expr = (f"arrayConcat(arraySlice(__{v}, 1+{offset}), arrayWithConstant({offset}, NULL)) AS v{varg}",)
    return (select_expr, arr_join_expr)

@ast_protect_injection
def vectorDenseRank(v):
    varg = random.randint(1,sys.maxsize)
    select_expr = f'v{varg}'
    arr_join_expr = (f'arrayEnumerateDense(__{v}) AS v{varg}',)
    return (select_expr, arr_join_expr)

@ast_protect_injection
def vectorCumeDist(v):
    varg = random.randint(1,sys.maxsize)
    select_expr = f'v{varg}_1 / v{varg}_2'
    arr_join_expr = (f'arrayEnumerate(__{v}) AS v{varg}_1',
                     f'arrayWithConstant(length(__{v}), length(__{v})) AS v{varg}_2',)
    return (select_expr, arr_join_expr)

@ast_protect_injection
def vectorPercentRank(v):
    varg = random.randint(1,sys.maxsize)
    select_expr = f'v{varg}_1 / v{varg}_2'
    arr_join_expr = (f'arrayConcat([0], arrayEnumerate(arraySlice(__{v}, 2))) AS v{varg}_1',
                     f'arrayWithConstant(length(__{v}), length(__{v}) - 1) AS v{varg}_2',)
    return (select_expr, arr_join_expr)

@ast_protect_injection
def vectorMap(func, v):
    varg = random.randint(1,sys.maxsize)
    func = str(func).strip("'")
    select_expr = f'{func}(v{varg})'
    arr_join_expr = (f'__{v} AS v{varg}',)
    return (select_expr, arr_join_expr)

@ast_protect_injection
def vectorNth(v, offset=1):
    varg = random.randint(1,sys.maxsize)
    select_expr = f'v{varg}'
    arr_join_expr = (f'arrayWithConstant(length(__{v}), (__{v})[{offset}]) AS v{varg}',)
    return (select_expr, arr_join_expr)

@ast_protect_injection
def vectorNtile(v, buckets):
    varg = random.randint(1,sys.maxsize)
    select_expr = f'ceil(v{varg}_2 / v{varg}_1)'
    arr_join_expr = (f'arrayWithConstant(length(__{v}), (length(__{v})/{buckets})) AS v{varg}_1',
                     f'arrayEnumerate(__{v}) AS v{varg}_2',)
    return (select_expr, arr_join_expr)

@ast_protect_injection
def vectorRank(v):
    varg = random.randint(1,sys.maxsize)
    select_expr = f'v{varg}_2 - v{varg}_1 + 1'
    arr_join_expr = (f'arrayEnumerateUniq(__{v}) AS v{varg}_1',
                     f'arrayEnumerate(__{v}) AS v{varg}_2',)
    return (select_expr, arr_join_expr)
