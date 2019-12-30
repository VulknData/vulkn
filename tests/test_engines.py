# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from vulkn import engines


def test_engines_list_option():
    assert str(engines.ListOption('PRIMARY KEY', 'column1', 'column2')) == 'PRIMARY KEY (column1, column2)'

def test_engines_key_value_option():
    assert str(engines.KeyValueOption('SETTINGS', k='v')) == 'SETTINGS k=v'

def test_engines_simple_settings():
    assert str(engines.Simple(settings={'a':'b'})) == '() SETTINGS a=b'

def test_engines_memory_settings():
    assert str(engines.Memory(settings={'a':'b'})) == 'Memory() SETTINGS a=b'

def test_engines_memory():
    assert str(engines.Memory()) == 'Memory()'

def test_engines_stripelog():
    assert str(engines.StripeLog()) == 'StripeLog()'

def test_engines_mergetree_simple():
    assert str(engines.MergeTree()) == 'MergeTree() ORDER BY (tuple())'

def test_engines_mergetree():
    expected = 'MergeTree() PARTITION BY (xyz, abc) ORDER BY (id, timestamp) PRIMARY KEY (id, timestamp) SAMPLE BY (id%4) TTL (30) SETTINGS a=b'
    assert str(engines.MergeTree(
        partition_by=['xyz', 'abc'], order_by=['id','timestamp'], primary_key=['id', 'timestamp'], 
        sample_by=['id%4'], ttl=[30], settings={'a':'b'})) == expected
