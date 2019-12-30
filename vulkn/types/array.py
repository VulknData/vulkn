# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from vulkn.types.base import TypeBase, Literal, func, FunctionExpression, quote_literal
from vulkn.utils import item_index


class Array(TypeBase):
    _METHODS = {
        'length': 'String'
    }

    _HIGHER_ORDER = [
        'map', 'filter', 'count', 'exists', 'all', 'sum', 
        'first', 'first_index', 'cum_sum', 'sort','reverse_sort'
    ]

    def __getitem__(self, index):
        from vulkn.types.string import String

        start, stop = item_index(index)
        if stop is None:
            return String(func('arrayElement', self._value, start))
        else:
            return String(func('arraySlice', self._value, start, stop))

    def __getattr__(self, name: str):
        def _method(lambda_arg):
            func = 'array{}'.format(''.join(map(str.title, name.split('_'))))
            v = FunctionExpression(func, Literal(lambda_arg), quote_literal(self._value))
            return Array(v)

        if name in [m for m in self._HIGHER_ORDER]:
            return _method
        else:
            return super(Array, self).__getattr__(name)

    def arrayStringConcat(self, separator: str=''):
        from vulkn.types.string import String
        return String(func('arrayStringConcat', self._value, separator))

    join = arrayStringConcat
