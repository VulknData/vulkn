# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from fixtures import v
from vulkn.types import *


def _sql(val):
    return val.sql

def _results(val):
    return val.exec().to_records()

def _both(val):
    return (_sql(val), _results(val),)


def test_vector_simple_number_list(v):
    sql = 'SELECT [1,2,3] AS v'
    results = [{'v': '[1,2,3]'}]
    assert _both(Vector([1,2,3]).alias('list_of_numbers')) == (sql, results)


def test_vector_simple_word_list(v):
    sql = "SELECT ['abc','def'] AS v"
    results = [{'v': "['abc','def']"}]
    assert _both(Vector(['abc', 'def']).alias('list_of_words')) == (sql, results)


def test_vector_range_simple(v):
    sql = 'SELECT number + 1 AS v FROM numbers_mt(toUInt64(1 + abs(1 - 100)))'
    results = [
        {'v': 
        '[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100]'}]
    assert _both(Vector.range(1, 100).alias('range_1_100'))[1] == results


def test_vector_range_negative(v):
    sql = 'SELECT number + -4 AS v FROM numbers_mt(toUInt64(1 + abs(-4 - -1)))'
    results = [{'v': '[-4,-3,-2,-1]'}]
    assert _both(Vector.range(-4, -1).alias('range_4_1'))[1] == results

"""
test(Vector.range(0,9).alias('range_0_9'))
test(Vector.rand(10, 100, 10).alias('rand_10_100_10'))
test(Vector
        .rand(
            DateTime.now().cast('UInt32') - 10000000,
            DateTime.now().cast('UInt32'), 100)
        .cast('DateTime')
        .alias('rand_dates')
        .sort_reverse())
test(Vector
        .rand(
            DateTime.now().cast('UInt32') - 10000000,
            DateTime.now().cast('UInt32'), 100)
        .cast('DateTime')
        .alias('cut_values')
        .sort()
        .cut(5))
test(Vector.range(0,9).take(30).alias('take_30'))
test(Vector.range(0,9).take(30).cut(4).flatten().alias('flatten'))
test(Vector.range(0,9).prev().alias('prev'))
test(Vector.range(0,9).next().alias('next'))
test(Vector.range(0,9).move(3).alias('move_forward'))
test(Vector.range(0,9).move(-3).alias('move_backward'))
test(Vector.range(0,9).delta().alias('delta'))
test(Vector.range(0,9).derivative(Vector.range(102,111)).alias('derivative'))
test(Vector.range(0,9).join(Vector.range(102,111)).alias('join'))
test(Vector.range(0,9).wavg(Vector.range(102,111)).alias('wavg'))
test(Vector.norm(75, 5, 1000).alias('norm'))
test(Vector.range(0,9).map('round').alias('map'))
test(Vector.range(0,9).maplag('divide').alias('map'))
test(Vector.range(0,9).maplead('divide').alias('map'))
"""
