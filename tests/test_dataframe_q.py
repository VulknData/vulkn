# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from fixtures import v
from vulkn.dataframe import WriteMode


def test_str_format(v):
    assert v.q('select {num:UInt8}').exec(num=3).to_records() == [{'3':3}]

def test_q_simple(v):
    assert v.q('select 1').exec().to_records() == [{'1':1}]

def test_q_limit(v):
    r = [{'number':i} for i in range(10)]
    assert v.q('select number from numbers(10)').limit(10).e().to_records() == r

def test_q_head(v):
    r = [{'number':i} for i in range(3)]
    assert v.q('select number from numbers(10)').head(3).e().to_records() == r

def test_q_first(v):
    r = [{'number':i} for i in range(1)]
    assert v.q('select number from numbers(10)').first().e().to_records() == r

def test_q_where(v):
    r = [{'number':3}]
    assert v.q('select number from numbers(10)').where('number = 3').e().to_records() == r

def test_q_filter(v):
    r = [{'number':3}]
    assert v.q('select number from numbers(10)').filter('number = 3').e().to_records() == r

def test_q_sort_desc(v):
    r = [{'number': n} for n in list(reversed(range(10)))]
    assert v.q('select number from numbers(10)').sort('number DESC').e().to_records() == r

def test_q_sort_asc(v):
    r = [{'number': n} for n in list(range(10))]
    assert v.q('select number from numbers(10)').sort('number').e().to_records() == r

def test_q_orderby_desc(v):
    r = [{'number': n} for n in list(reversed(range(10)))]
    assert v.q('select number from numbers(10)').orderBy('number DESC').e().to_records() == r

def test_q_orderby_asc(v):
    r = [{'number': n} for n in list(range(10))]
    assert v.q('select number from numbers(10)').orderBy('number').e().to_records() == r

def test_q_distinct(v):
    r = [{'number': 1}]
    assert v.q('select distinct arrayJoin([1,1,1]) as number').e().to_records() == r

def test_q_show_sql(v):
    r = 'SELECT count() FROM numbers(10);'
    assert v.q(r).show_sql() == r

def test_q_cache_query(v):
    import vulkn.dataframe
    r = [{'number': n} for n in list(range(10))]
    df = v.q('select number from numbers(10)').cache()
    assert isinstance(df, vulkn.dataframe.SelectQueryDataFrame)
    assert df.show_sql().startswith('SELECT * FROM vulkn.session_')
    assert df.e().to_records() == r

def test_q_write_table_create(v):
    r = [{'number': n} for n in list(range(10))]
    assert v.t().s is None
    df = v.q('select number from numbers(10)').write('default','table_create')
    assert df.select('*').e().to_records() == r

def test_q_write_table_append(v):
    r = [{'number': n} for n in list(range(10))]
    assert v.t().s is None
    df = v.q('select number from numbers(10)').write('default','table_append')
    assert df.select('*').e().to_records() == r
    r = [{'number': n} for n in list(range(20))]
    df = (v
        .q('select number from numbers(20) where number > 9')
        .write('default','table_append', mode=WriteMode.Append))
    assert df.select('*').e().to_records() == r