# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from vulkn.types.numeric import Numeric

class Float(Numeric):
    pass


class Float32(Float):
    TYPE = 'Float32'
    CAST = 'Float32'


class Float64(Float):
    TYPE = 'Float64'
    CAST = 'Float64'
    _METHODS = {
        'exp': 'Integer',
        'negate': 'Integer'}

    def e(self):
        return Float64(Literal('e()'))

    def pi(self):
        return Float64(Literal('pi()'))