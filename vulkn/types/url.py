# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from vulkn.types.base import func
from vulkn.types.array import Array
from vulkn.types.string import String
from vulkn.types.integer import UInt64


class URL(String):
    _METHODS = {
        'protocol': None,
        'domain': None,
        'domainWithoutWWW': None,
        'topLevelDomain': None,
        'firstSignificantSubdomain': None,
        'cutToFirstSignificantSubdomain': None,
        'path': None,
        'pathFull': None,
        'queryString': None,
        'fragment': None,
        'queryStringAndFragment': None,
        'extractURLParameters': Array,
        'extractURLParameterNames': Array,
        'URLHierarchy': Array,
        'URLPathHierarchy': Array,
        'decodeURLComponent': Array,
        'cutWWW': None,
        'cutQueryString': None,
        'cutFragment': None,
        'cutQueryStringAndFragment': None,
    }

    def extractURLParameter(self, name):
        return URL(func('extractURLParameter', self._value, name))

    def cutURLParameter(self, name):
        return URL(func('cutURLParameter', self._value, name))

    def URLHash(self, N=None):
        if N:
            return UInt64(func('cutURLParameter', self._value, N))
        else:
            return UInt64(func('cutURLParameter', self._value))