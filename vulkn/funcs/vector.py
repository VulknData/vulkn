# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from vulkn.types.base import func
from vulkn.types import UInt64, UInt8, Array, col


def vectorWindow(v, backward=None, forward=None):
    return col(func('vectorWindow', v, backward, forward))

def vectorWindowAgg(agg, v, backward=None, forward=None):
    return col(func('vectorWindowAgg', v, backward, forward))

def vectorDeltaLag(v, offset=1):
    return col(func('vectorDeltaLag', v, offset))

def vectorDeltaLead(v, offset=1):
    return col(func('vectorDeltaLead', v, offset))

vectorDelta = vectorDeltaLag

def vectorRowNumber():
    return col(func('vectorRowNumber'))

vectorRowNum = vectorRowNumber

def vectorAgg(agg, v):
    return col(func('vectorAgg', agg, v))

def vectorFirst(v):
    return col(func('vectorFirst', v))

def vectorLast(v):
    return col(func('vectorLast', v))

def vectorLag(v, offset=-1):
    return col(func('vectorLag', v, offset))

def vectorLead(v, offset=1):
    return col(func('vectorLead', v, offset))

def vectorDenseRank(v):
    return col(func('vectorDenseRank', v))

def vectorCumeDist(v):
    return col(func('vectorCumeDist', v))

def vectorPercentRank(v):
    return col(func('vectorPercentRank', v))

def vectorMap(func, v):
    return col(func('vectorMap', func, v))

def vectorNth(v, offset=1):
    return col(func('vectorNth', v, offset))

def vectorNtile(v, buckets):
    return col(func('vectorNtile', v, buckets))

def vectorRank(v):
    return col(func('vectorRank', v))
