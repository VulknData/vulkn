# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from fixtures import v
from vulkn.dataframe import WriteMode


def test_show_sql_single_column_no_table(v):
    assert v.q('select 1').show_sql() == 'SELECT 1;'

def test_show_sql_multiple_columns_no_table(v):
    assert v.q('select 1, 2').show_sql() == 'SELECT 1, 2;'

def test_show_sql_string_no_table(v):
    assert v.q("select 'string'").show_sql() == "SELECT 'string';"

def test_basic_exec(v):
    assert v.q('select 1').exec().to_records() == [{'1':1}]

def test_str_format(v):
    assert v.q('select {num:UInt8}').exec(num=3).to_records() == [{'3':3}]

def test_dataframe_simple(v):
    assert v.select(1).exec().to_records() == [{'1':1}]
