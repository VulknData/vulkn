# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from vulkn.types.base import func
from vulkn.types import String, Array


def hex(arg):
    return String(func('hex', arg))

def unhex(arg):
    return String(func('unhex', arg))

def UUIDStringToNum(arg):
    return String(func('UUIDStringToNum', arg))

def UUIDNumToString(arg):
    return String(func('UUIDNumToString', arg))

def bitmaskToList(arg):
    return String(func('bitmaskToList', arg))

def bitmaskToArray(arg):
    return Array(func('bitmaskToArray', arg))
