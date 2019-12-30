# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from vulkn.types.base import func, Literal
from vulkn.types.numeric import Numeric


class Integer(Numeric):
    _METHODS = {
        'abs': 'Integer',
        'negate': 'Integer',
        'sum': None}

    def plus(self, right):
        return Integer(func('plus', self._value, right))

    def minus(self, right):
        return Integer(func('minus', self._value, right))

    def multiply(self, right):
        return Integer(func('multiply', self._value, right))

    def divide(self, right):
        return Integer(func('divide', self._value, right))

    def intDiv(self, right):
        return Integer(func('intDiv', self._value, right))

    def intDivOrZero(self, right):
        return Integer(func('intDivOrZero', self._value, right))

    def modulo(self, right):
        return Integer(func('modulo', self._value, right))

    def gcd(self, right):
        return Integer(func('gcd', self._value, right))

    def lcm(self, right):
        return Integer(func('lcm', self._value, right))

    def vectorAccumulate(self):
        return Integer(func('vectorAccumulate', Literal('__{}'.format(str(self._value)[1:-1]))))


class Int8(Integer):
    MIN = -128
    MAX = 127
    TYPE = 'Int8'
    CAST = 'Int8'


class Int16(Integer):
    MIN = -32768
    MAX = 32767
    TYPE = 'Int16'
    CAST = 'Int16'


class Int32(Integer):
    MIN = -2147483648
    MAX = 2147483647
    TYPE = 'Int32'
    CAST = 'Int32'


class Int64(Integer):
    MIN = -9223372036854775808
    MAX = 9223372036854775807
    TYPE = 'Int64'
    CAST = 'Int64'


class UInt8(Integer):
    MIN = 0
    MAX = 255
    TYPE = 'UInt8'
    CAST = 'UInt8'


class UInt16(Integer):
    MIN = 0
    MAX = 65535
    TYPE = 'UInt16'
    CAST = 'UInt16'


class UInt32(Integer):
    TYPE = 'UInt32'
    CAST = 'UInt32'
    _METHODS = {
        'IPv4NumToString': 'String',
        'IPv4NumToStringClassC': 'String',
        'IPv6NumToString': 'String',
        'rand': None,
        'randConstant': None}
    MIN = 0
    MAX = 4294967295


class UInt64(Integer):
    TYPE = 'UInt64'
    CAST = 'UInt64'
    _METHODS = {
        'rand64': None,
        'intExp2': None,
        'intExp10': None,
        'sum': None}
    MIN = 0
    MAX = 18446744073709551615
