# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from fixtures import v
from vulkn.datatable import WriteMode


def test_range_table_function(v):
    expected = [{'range': -2}, {'range': -1}, {'range': 0}, {'range': 1}, {'range': 2}, 
        {'range': 3}, {'range': 4}, {'range': 5}, {'range': 6}, {'range': 7}, {'range': 8}]
    start = -2
    end = 8
    assert v.range(start, end).exec().to_records() == expected

def test_range_system_table(v):
    expected = [{'range': -2}, {'range': -1}, {'range': 0}, {'range': 1}, {'range': 2}, 
        {'range': 3}, {'range': 4}, {'range': 5}, {'range': 6}, {'range': 7}, {'range': 8}]
    start = -2
    end = 8
    assert v.range(start, end, True).exec().to_records() == expected

def test_range_system_table_multi_threaded(v):
    expected = [{'range': -2}, {'range': -1}, {'range': 0}, {'range': 1}, {'range': 2}, 
        {'range': 3}, {'range': 4}, {'range': 5}, {'range': 6}, {'range': 7}, {'range': 8}]
    start = -2
    end = 8
    assert v.range(start, end, True, True).exec().to_records() == expected