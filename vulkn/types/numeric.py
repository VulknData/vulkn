# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from vulkn.types.base import TypeBase, func


class Numeric(TypeBase):
    _METHODS = {
        'exp': 'Float64',
        'log': 'Float64',
        'exp2': 'Float64',
        'log2': 'Float64',
        'exp10': 'Float64',
        'log10': 'Float64',
        'sqrt': 'Float64',
        'cbrt': 'Float64',
        'erf': 'Float64',
        'erfc': 'Float64',
        'lgamma': 'Float64',
        'tgamma': 'Float64',
        'sin': 'Float64',
        'cos': 'Float64',
        'tan': 'Float64',
        'asin': 'Float64',
        'acos': 'Float64',
        'atan': 'Float64',
        'roundToExp2': None,
        'roundDuration': None,
        'roundAge': None,
        'abs': None,
        'negate': None}

    def pow(self, right):
        return Float64(func('pow', self._value, right))

    def plus(self, right):
        return type(self)(func('plus', self._value, right))

    def minus(self, right):
        return type(self)(func('minus', self._value, right))

    def multiply(self, right):
        return type(self)(func('multiply', self._value, right))

    def divide(self, right):
        return type(self)(func('divide', self._value, right))

    def intDiv(self, right):
        return type(self)(func('intDiv', self._value, right))

    def intDivOrZero(self, right):
        return type(self)(func('intDivOrZero', self._value, right))

    def modulo(self, right):
        return type(self)(func('modulo', self._value, right))

    def gcd(self, right):
        return type(self)(func('gcd', self._value, right))

    def lcm(self, right):
        return type(self)(func('lcm', self._value, right))

    def floor(self, N: int=0):
        return type(self)(func('floor', self._value, N))
    
    def ceil(self, N: int=0):
        return type(self)(func('ceil', self._value, N))
    
    def round(self, N: int=0):
        return type(self)(func('round', self._value, N))

    def roundDown(self, arr):
        return type(self)(func('roundDown', self._value, arr))

    def __truediv__(self, right) -> any:
        return type(self)(func('divide', self._value, right))

    def __add__(self, right) -> any:
        return type(self)(func('plus', self._value, right))

    def __sub__(self, right) -> any:
        return type(self)(func('minus', self._value, right))

    def __mul__(self, right) -> any:
        return type(self)(func('multiply', self._value, right))

    def __floordiv__(self, right) -> any:
        return type(self)(self/right).floor()

    def __mod__(self, right) -> any:
        return type(self)(func('modulo', self._value, right))

    def __pow__(self, right) -> any:
        return type(self)(func('pow', self._value, right))

    def bitAnd(self, right) -> any:
        return type(self)(func('bitAnd', self._value, right))

    def bitOr(self, right) -> any:
        return type(self)(func('bitOr', self._value, right))
    
    def bitXor(self, right) -> any:
        return type(self)(func('bitXor', self._value, right))

    def bitNot(self) -> any:
        return type(self)(func('bitNot', self._value))

    def bitShiftLeft(self, right) -> any:
        return type(self)(func('bitShiftLeft', self._value, right))

    __lshift__ = bitShiftLeft

    def bitShiftRight(self, right) -> any:
        return type(self)(func('bitShiftRight', self._value, right))

    __rshift__ = bitShiftRight

    def bitRotateLeft(self, right) -> any:
        return type(self)(func('bitRotateLeft', self._value, right))

    def bitRotateRight(self, right) -> any:
        return type(self)(func('bitRotateRight', self._value, right))

    def bitTest(self, right) -> any:
        return type(self)(func('bitTest', self._value, right))

    def bitTestAll(self, right) -> any:
        return type(self)(func('bitTestAll', self._value, right))

    def bitTestAny(self, right) -> any:
        return type(self)(func('bitTestAny', self._value, right))