# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from vulkn.types.base import func
from vulkn.types import UInt64, UInt8, Array, col


def bitmapBuild(array):
    return col(func('bitmapBuild', array))

def bitmapToArray(bitmap):
    return Array(func('bitmapToArray', bitmap))

def bitmapSubsetInRange(bitmap, range_start, range_end):
    return col(func('bitmapSubsetInRange', bitmap, range_start, range_end))

def bitmapContains(haystack, needle):
    return UInt8(func('bitmapContains', haystack, needle))

def bitmapHasAny(bitmap1, bitmap2):
    return UInt8(func('bitmapHasAny', bitmap1, bitmap2))

def bitmapHasAll(bitmap1, bitmap2):
    return UInt8(func('bitmapHasAll', bitmap1, bitmap2))

def bitmapAnd(bitmap1, bitmap2):
    return col(func('bitmapAnd', bitmap1, bitmap2))

def bitmapOr(bitmap1, bitmap2):
    return col(func('bitmapOr', bitmap1, bitmap2))

def bitmapXor(bitmap1, bitmap2):
    return col(func('bitmapXor', bitmap1, bitmap2))

def bitmapAndnot(bitmap1, bitmap2):
    return col(func('bitmapAndnot', bitmap1, bitmap2))

def bitmapCardinality(bitmap):
    return UInt64(func('bitmapCardinality', bitmap))

def bitmapAndCardinality(bitmap1, bitmap2):
    return UInt64(func('bitmapAndCardinality', bitmap1, bitmap2))

def bitmapOrCardinality(bitmap1, bitmap2):
    return UInt64(func('bitmapOrCardinality', bitmap1, bitmap2))

def bitmapXorCardinality(bitmap1, bitmap2):
    return UInt64(func('bitmapXorCardinality', bitmap1, bitmap2))

def bitmapAndnotCardinality(bitmap1, bitmap2):
    return UInt64(func('bitmapAndnotCardinality', bitmap1, bitmap2))
