# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


# TODO: Next release.

class Tuple:
    def __init__(self, *args, keys=True):
        self._column = None
        self._tuple = args
        self._use_keys = keys

    def __getattr__(self, key):
        try:
            return self._tuple[key]
        except KeyError:
            raise AttributeError

    @classmethod
    def c(self, column, keys):
        t = Tuple()
        t._column = column
        t._use_keys = True
        t._keys = keys
        structure
        return t


"""
k = Tuple(['a','b']).alias('z')
(k['a'] / k['d'])

df.select(
    Tuple.c('q', structure=[('a','b'),('c','d')]))
"""