# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from vulkn.types.base import Literal
from vulkn.types.string import String


class UUID(String):
    TYPE = 'String'
    CAST = 'String'
    _METHODS = {
        'UUIDStringToNum': 'String',
        'UUIDNumToString': 'String'
    }

    @staticmethod
    def generateUUIDv4():
        return UUID(Literal('generateUUIDv4()'))

    UUIDv4 = generateUUIDv4