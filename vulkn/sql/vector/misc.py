# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import sys
import random
import logging

from vulkn.sql.utils import ast_protect_injection


log = logging.getLogger()


@ast_protect_injection
def vectorWindow(v, backward=None, forward=None):
    varg = random.randint(1,sys.maxsize)
    select_expr = []
    arr_join_expr = []
    if backward is None and forward is None:
        return (f'[v{varg}]', (f'{v} AS v{varg}',))
    backward = int(str(backward or 0))
    forward = int(str(forward or 0))
    if int(str(forward)) < int(str(backward)):
        raise Exception('vectorWindow forward must be greater than backwards.')
    for idx, i in enumerate(range(backward, forward+1)):
        select_expr.append(f"v{varg}_{idx+1}")
        if i < 0:
            arr_join_expr.append(
                f"arrayConcat(arrayWithConstant(abs({i}), NULL), arraySlice(__{v}, 1, {i})) AS v{varg}_{idx+1}")
        elif i == 0:
            arr_join_expr.append(f"__{v} AS v{varg}_{idx+1}")
        else: # i > 0
            arr_join_expr.append(
                f"arrayConcat(arraySlice(__{v}, 1+{i}), arrayWithConstant(abs({i}), NULL)) AS v{varg}_{idx+1}")
    return ("[{}]".format(','.join(select_expr)), arr_join_expr)

@ast_protect_injection
def vectorWindowAgg(agg, v, backward=None, forward=None):
    w = vectorWindow(v, backward, forward)
    varg = w[0]
    return (f"arrayReduce('{agg}', {varg})", w[1])

@ast_protect_injection
def vectorDeltaLag(v, offset=1):
    offset = int(str(offset))
    if offset < 1:
        raise Exception('Parameter "offset" must be greater than 0')
    varg = random.randint(1,sys.maxsize)
    select_expr = f'v{varg}_1 - v{varg}_2'
    arr_join_expr = (f'__{v} AS v{varg}_1',
                     f"arrayConcat(arrayWithConstant({offset}, NULL), arraySlice(__{v}, {offset}, -{offset})) AS v{varg}_2",)
    return (select_expr, arr_join_expr)

@ast_protect_injection
def vectorDeltaLead(v, offset=1):
    offset = int(str(offset))
    if offset < 1:
        raise Exception('Parameter "offset" must be greater than 0')
    varg = random.randint(1,sys.maxsize)
    select_expr = f'v{varg}_2 - v{varg}_1'
    arr_join_expr = (f'__{v} AS v{varg}_1',
                     f"arrayConcat(arraySlice(__{v}, 1+{offset}), arrayWithConstant({offset}, NULL)) AS v{varg}_2",)
    return (select_expr, arr_join_expr)

vectorDelta = vectorDeltaLag

# TODO: Performance problems. Leaving disabled.
# @ast_protect_injection
# def vectorAccumulate(v):
#    varg = random.randint(1,sys.maxsize)
#    return (f'runningAccumulate(v{varg})', (f"arrayReduce('sumStateForEach', [__{v}]) AS v{varg}",))
