# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from vulkn.types.base import func
from vulkn.types import String, Array, Float64, UInt8, col, UInt64


def greatCircleDistance(lon1Deg, lat1Deg, lon2Deg, lat2Deg):
    return Float64(func('greatCircleDistance', lon1Deg, lat1Deg, lon2Deg, lat2Deg))

def pointInEllipses(*args):
    return UInt8(func('pointInEllipses', *args))

def pointInPolygon(point, vertices, polygons=None):
    if polygons:
        return UInt8(func('pointInPolygon', point, vertices, polygons))
    return UInt8(func('pointInPolygon', point, vertices))

def geohashEncode(longitude, latitude, precision=None):
    if precision:
        return String(func('geohashEncode', longitude, latitude, precision))
    return String(func('geohashEncode', longitude, latitude))

def geohashDecode(geohash):
    return col(func('geohashDecode', geohash))

def geoToH3(longitude, latitude, resolution):
    return UInt64(func('geoToH3', longitude, latitude, resolution))

def geohashesInBox(longitude_min, latitude_min, longitude_max, latitude_max, precision):
    return Array(
        func('geohashesInBox', longitude_min, latitude_min, longitude_max, latitude_max, precision))