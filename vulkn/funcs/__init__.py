# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from functools import partial


from vulkn.types.base import quote_literal, func, TypeBase, Literal
from vulkn.types import String, col, c
import vulkn.funcs.bitmap as bitmap
import vulkn.funcs.encode as encode
import vulkn.funcs.geo as geo
import vulkn.funcs.agg as agg
import vulkn.funcs.vector as vector


def coalesce(*args):
    return c('coalesce({})'.format(', '.join(map(str, args))))

def and_(*args):
    return c('({})'.format(' AND '.join(map(str, args))))

def or_(*args):
    return c('({})'.format(' OR '.join(map(str, args))))

def not_(args):
    return c('NOT ({})'.format(str(args)))

def xor_(*args):
    return c('({})'.format(' XOR '.join(map(str, args))))

def if_(condition, then_arg, else_arg):
    return c('if({}, {}, {})'.format(condition, quote_literal(then_arg), quote_literal(else_arg)))

def multiIf(branches, default):
    r = 'multiIf({branches}, {default})'
    b_stmts = []
    for branch in branches:
        b_stmts.append('{}, {}'.format(branch[0], quote_literal(branch[1])))
    return c(r.format(branches=', '.join(b_stmts), default=quote_literal(default)))

switch = multiIf

def arrayJoin(arr):
    return c('arrayJoin({})'.format(str(arr)))

def arrayGeneric(func_name, *args):
    lambda_exp = (args[0] if (callable(args[0]) or hasattr(args[0], '__call__')) else None)
    params = (None if lambda_exp is None else '({})'.format(', '.join(lambda_exp.__code__.co_varnames)))
    arrs = args if lambda_exp is None else args[1:]
    arrs = ', '.join([str(a) for a in arrs])
    r = ('{func_name}({arrs})' if lambda_exp is None else '{func_name}({params} -> {lambda_exp}, {arrs})')
    s = ''
    if lambda_exp:
        s = r.format(func_name=func_name, params=params, lambda_exp=lambda_exp(), arrs=arrs)
    else:
        s = r.format(func_name=func_name, arrs=arrs)
    return c(s)

arrayMap = partial(arrayGeneric, 'arrayMap')
arrayFilter = partial(arrayGeneric, 'arrayFilter')
arrayCount = partial(arrayGeneric, 'arrayCount')
arrayExists = partial(arrayGeneric, 'arrayExists')
arrayAll = partial(arrayGeneric, 'arrayAll')
arraySum = partial(arrayGeneric, 'arraySum')
arrayFirst = partial(arrayGeneric, 'arrayFirst')
arrayFirstIndex = partial(arrayGeneric, 'arrayFirstIndex')
arrayCumSum = partial(arrayGeneric, 'arrayCumSum')
arrayCumSumNonNegative = partial(arrayGeneric, 'arrayCumSumNonNegative')
arraySort = partial(arrayGeneric, 'arraySort')
arrayReverseSort = partial(arrayGeneric, 'arrayReverseSort')

def formatReadableSize(bytes):
    return String(func('formatReadableSize', bytes))
