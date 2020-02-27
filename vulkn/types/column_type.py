# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from enum import Enum, unique


def nan_to_none(value):
    try:
        if pd.np.isnan(value):
            return None
    except:
        pass
    return value


class ColumnType:
    @unique
    class DefaultKind(Enum):
        MATERIALIZED = 'MATERIALIZED'
        ALIAS = 'ALIAS'
        DEFAULT = 'DEFAULT'
        NONE = None

    def __init__(self, name, col_type, default_kind=None, default_expression=None, compression_codec=None):
        self._name = name
        self._col_type = col_type
        self._default_kind = nan_to_none(default_kind)
        self._default_expression = nan_to_none(default_expression)
        self._compression_codec = nan_to_none(compression_codec)
    
    def __repr__(self):
        _none_or_quoted = lambda value: 'None' if value is None else "'{}'".format(value)
        r = 'ColumnType({name}, {col_type}, default_kind={default_kind}, default_expression={default_expression} compression_codec={compression_codec})'
        return r.format(name="'{}'".format(self._name),
                        col_type="'{}'".format(self._col_type),
                        default_kind=_none_or_quoted(self._default_kind),
                        default_expression=_none_or_quoted(self._default_expression),
                        compression_codec=_none_or_quoted(self._compression_codec))

    def __str__(self):
        _none_or_quoted = lambda value: '' if value is None else "{}".format(value)
        opts = ' '.join(filter(lambda x: x is not None,
                        [_none_or_quoted(self._default_kind), _none_or_quoted(self._default_expression), _none_or_quoted(self._compression_codec)]))
        return '{name} {col_type}{opts}'.format(name=self._name,
                                                col_type=self._col_type,
                                                opts=opts if len(opts) > 0 else '')
