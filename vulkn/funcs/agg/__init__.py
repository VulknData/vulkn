# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from vulkn.types.base import func
from vulkn.types import *


def count(expression=None, distinct=False):
    if distinct and expression:
        return UInt64(func('countDistinct', expression))
    if expression:
        return UInt64(func('count', expression))
    return UInt64(func('count'))

def any(x):
    return col(func('any', x))

def anyHeavy(x):
    return col(func('anyHeavy', x))

def anyLast(x):
    return col(func('anyLast', x))

def groupBitAnd(expr):
    return UInt64(func('groupBitAnd', expr))

def groupBitOr(expr):
    return UInt64(func('groupBitOr', expr))

def groupBitXor(expr):
    return UInt64(func('groupBitXor', expr))

def groupBitmap(expr):
    return UInt64(func('groupBitmap', expr))

def min(x):
    return col(func('min', x))

def max(x):
    return col(func('max', x))

def argMin(arg, val):
    return col(func('argMin', arg, val))

def argMax(arg, val):
    return col(func('argMax', arg, val))

def sum(x):
    return col(func('sum', x))

def sumWithOverflow(x):
    return col(func('sumWithOverflow', x))

def sumMap(key, value):
    return col(func('sumMap', key, value))

def skewPop(x):
    return Float64(func('skewPop', x))

def skewSamp(x):
    return Float64(func('skewSamp', x))

def kurtPop(x):
    return Float64(func('any', x))

def kurtSamp(x):
    return Float64(func('kurtSamp', x))

def timeSeriesGroupSum(uid, timestamp, value):
    return Array(func('timeSeriesGroupSum', uid, timestamp, value))

def timeSeriesGroupRateSum(uid, ts, val):
    return Array(func('timeSeriesGroupRateSum', uid, ts, val))

def avg(x):
    return Float64(func('avg', x))

def uniq(*args):
    return UInt64(func('uniq', *args))

def uniqCombined(*args):
    return UInt64(func('uniqCombined', *args))

def uniqHLL12(*args):
    return UInt64(func('uniqHLL12', *args))

def uniqExact(*args):
    return UInt64(func('uniqExact', *args))

def groupArray(x, max_size=None):
    if max_size:
        return Array(func('groupArray({})'.format(max_size), x))
    return Array(func('groupArray', x))

def groupArrayInsertAt(position, x):
    return Array(func('groupArrayInsertAt', position, x))

def groupArrayMovingSum(x, window_size=None):
    if window_size:
        Array(func('groupArrayMovingSum({})'.format(window_size), x))
    return Array(func('groupArrayMovingSum', x))

def groupArrayMovingAvg(x, window_size=None):
    if window_size:
        Array(func('groupArrayMovingAvg({})'.format(window_size), x))
    return Array(func('groupArrayMovingAvg', x))

def groupUniqArray(x, max_size=None):
    if max_size:
        return Array(func('groupUniqArray({})'.format(max_size), x))
    return Array(func('groupUniqArray', x))

def quantile(level, x):
    return col(func('quantile({})'.format(level), x))

def quantileDeterministic(level, x, determinator):
    return col(func('quantileDeterministic', level, x, determinator))

def quantileTiming(level, expression):
    return col(func('quantile({})'.format(level), expression))

def quantileTimingWeighted(level, x, weight):
    return col(func('quantileTimingWeighted', level, x, weight))

def quantileExact(level, x):
    return col(func('quantileExact({})'.format(level), x))

def quantileExactWeighted(level, x, weight):
    return col(func('quantileExactWeighted', level, x, weight))

def quantileTDigest(level, x):
    return col(func('quantileTDigest({})'.format(level), x))

def median(x):
    return col(func('median', x))

# TODO Next release. Add median variants.

def quantiles(levels, x):
    return Array(func('quantiles', *levels, x))

# TODO Next release. Add quantiles variants.

def varSamp(x):
    return Float64(func('varSamp', x))

def varPop(x):
    return Float64(func('varPop', x))

def stddevSamp(x):
    return Float64(func('stddevSamp', x))

def stddevPop(x):
    return Float64(func('stddevPop', x))

def topK(N, column):
    return col(func('topK({})'.format(N), column))

def covarSamp(x, y):
    return Float64(func('covarSamp', x, y))

def covarPop(x, y):
    return Float64(func('covarPop', x, y))

def corr(x, y):
    return Float64(func('corr', x, y))

def histogram(bins, values):
    return Array(func('histogram', bins, values))

def sequenceMatch(pattern, time, conditions):
    return col(func('sequenceMatch', pattern, time, *conditions))

def sequenceCount(pattern, time, conditions):
    return UInt64(func('sequenceCount', pattern, time, *conditions))

def windowFunnel(window, timestamp, conditions):
    return UInt64(func('windowFunnel', window, timestamp, *conditions))

def retention(*conditions):
    return UInt8(func('retention', *conditions))

def uniqUpTo(N, x):
    return UInt64(func('uniqUpTo', N, x))

def sumMapFiltered(keys_to_keep, keys, values):
    return col(func('sumMapFiltered', keys_to_keep, keys, values))

"""
class AggregateFunction:
    def __init__(self, *args):
        pass

    @classmethod
    def If(self, cond):
        r = AggregateFunction(self._func, self._args)
        r._if = True
        return r

    @classmethod
    def Array(self):
        r = AggregateFunction(self._func, self._args)
        r._array = True
        return r

    @classmethod
    def State(self):
        r = AggregateFunction(self._func, self._args)
        r._state = True
        return r

    @classmethod
    def Merge(self):
        r = AggregateFunction(self._func, self._args)
        r._merge = True
        return r
    
    @classmethod    
    def MergeState(self):
        r = AggregateFunction(self._func, self._args)
        r._merge_state = True
        return r

    @classmethod
    def ForEach(self):
        r = AggregateFunction(self._func, self._args)
        r._for_each = True
        return r

    @classmethod
    def Resample(self, start, end, stop):
        r = AggregateFunction(self._func, self._args)
        r._resample = True
        return r

    def __str__(self):
        return str(self._value)
"""