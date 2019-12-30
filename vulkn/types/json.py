# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from vulkn.types.base import TypeBase, func, Literal
from vulkn.types.array import Array
from vulkn.types.integer import UInt8, UInt64, Int64
from vulkn.types.float import Float64
from vulkn.types.string import String


class JSON(TypeBase):
    TYPE = 'String'
    CAST = 'String'

    def visitParamHas(self, name):
        return UInt8(func('visitParamHas', self._value, name))

    def visitParamExtractUInt(self, name):
        return UInt64(func('visitParamExtractUInt', self._value, name))

    def visitParamExtractInt(self, name):
        return Int64(func('visitParamExtractInt', self._value, name))

    def visitParamExtractFloat(self, name):
        return Float64(func('visitParamExtractFloat', self._value, name))

    def visitParamExtractBool(self, name):
        return UInt8(func('visitParamExtractBool', self._value, name))

    def visitParamExtractRaw(self, name):
        return String(func('visitParamExtractRaw', self._value, name))

    def visitParamExtractString(self, name):
        return String(func('visitParamExtractString', self._value, name))

    has = visitParamHas
    getUInt = visitParamExtractUInt
    getInt = visitParamExtractInt
    getFloat = visitParamExtractFloat
    getBool = visitParamExtractBool
    getRaw = visitParamExtractRaw
    getString = visitParamExtractString

    def JSONHas(self, *indices_or_keys):
        return UInt8(func('JSONHas', self._value, *indices_or_keys))

    def JSONKey(self, key):
        return String(func('JSONKey', self._value, key))

    def JSONLength(self, *indices_or_keys):
        return UInt64(func('JSONLength', self._value, *indices_or_keys))

    def JSONType(self, *indices_or_keys):
        return String(func('JSONType', self._value, *indices_or_keys))

    def JSONExtractUInt(self, *indices_or_keys):
        return UInt64(func('JSONExtractUInt', self._value, *indices_or_keys))

    def JSONExtractInt(self, *indices_or_keys):
        return Int64(func('JSONExtractInt', self._value, *indices_or_keys))    
    
    def JSONExtractFloat(self, *indices_or_keys):
        return Float64(func('JSONExtractFloat', self._value, *indices_or_keys))

    def JSONExtractBool(self, *indices_or_keys):
        return UInt8(func('JSONExtractBool', self._value, *indices_or_keys))

    def JSONExtractString(self, *indices_or_keys):
        return String(func('JSONExtractString', self._value, *indices_or_keys))

    def JSONExtract(self, indices_or_keys, return_type):
        return TypeBase(Literal((func('JSONExtract', self._value, *indices_or_keys, return_type))))

    def JSONExtractKeysAndValues(self, *indices_or_keys, value_type):
        return TypeBase(Literal((func('JSONExtractKeysAndValues', self._value, *indices_or_keys, value_type))))

    def JSONExtractRaw(self, *indices_or_keys):
        return JSON(func('JSONExtractRaw', self._value, *indices_or_keys))
