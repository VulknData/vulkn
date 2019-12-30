# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from vulkn.types import *
from fixtures import v


def test_select_str_expression(v):
    df = v.numbers(10).select('count() AS c')
    assert df.exec().to_records() == [{'c':10}]

def test_select_col_container(v):
    df = v.numbers(10).select(c('count()').alias('c'))
    assert df.exec().to_records() == [{'c':10}]

def test_select_variant_system(v):
    df = v.numbers(10, True).select('*').select(c('count()').alias('c'))
    assert df.exec().to_records() == [{'c':10}]

def test_select_variant_system_mt(v):
    df = v.numbers(10, True, True).select('*').select(c('count()').alias('c'))
    assert df.exec().to_records() == [{'c':10}]
