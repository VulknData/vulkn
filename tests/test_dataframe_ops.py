# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from fixtures import v
from vulkn.types import *
from vulkn.dataframe import WriteMode


def test_dataframe_ops_select_single_column(v):
    df = v.select(c(1).alias('c'))
    assert df.exec().to_records() == [{'c':1}]

def test_dataframe_ops_select_multiple_columns(v):
    df = v.select(c(1).alias('col1'), c(2).alias('col2'))
    assert df.exec().to_records() == [{'col1':1,'col2':2}]

def test_dataframe_ops_with_select(v):
    df = v.with_('1 AS x').select((UInt64(n='x') + 2).alias('v'))
    assert df.exec().to_records() == [{'v':3}]

