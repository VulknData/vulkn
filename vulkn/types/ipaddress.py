# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from vulkn.types.base import func
from vulkn.types.array import Array
from vulkn.types.string import String
from vulkn.types.integer import UInt32, UInt64


class IP(String):
    def IPv4CIDRToRange(self, cidr):
        return tuple(func('IPv4CIDRToRange', cidr))

    def IPv6CIDRToRange(self, cidr):
        return tuple(func('IPv6CIDRToRange', cidr))

    @staticmethod
    def IPv4NumToString(num):
        return String(func('IPv4NumToString', num))

    @staticmethod
    def IPv6NumToString(num):
        return String(func('IPv6NumToString', num))

    @staticmethod
    def IPv4NumToStringClassC(num):
        return tuple(func('IPv4NumToStringClassC', num))

    @staticmethod
    def IPv6StringToNum(s):
        return String(func('IPv6StringToNum', s))

    @staticmethod
    def IPv4StringToNum(s):
        return UInt32(func('IPv4StringToNum', s))

    @staticmethod
    def IPv4ToIPv6(x):
        return String(func('IPv4ToIPv6', x))

    def cutIPv6(self, bitsToCutForIPv6, bitsToCutForIPv4):
        return String(func('cutIPv6', bitsToCutForIPv6, bitsToCutForIPv4))

    toIPv4 = IPv4StringToNum
    toIPv6 = IPv6StringToNum

    @staticmethod
    def MACNumToString(num):
        return String(func('MACNumToString', num))

    @staticmethod
    def MACStringToNum(mac):
        return UInt64(func('MACStringToNum', mac))

    @staticmethod
    def MACStringToOUI(mac):
        return UInt64(func('MACStringToOUI', mac))