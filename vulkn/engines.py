# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


class ListOption:
    def __init__(self, name, *options):
        self.name = name
        self.options = options

    def __str__(self):
        r = ''
        if len(self.options) > 0:
            parameters = ', '.join(list(map(str, self.options)))
            r = '{keyword} ({parameters})'.format(keyword=self.name, parameters=parameters)
        return r


class KeyValueOption:
    def __init__(self, name, **options):
        self.name = name
        self.options = options

    def __str__(self):
        r = ''
        if len(self.options) > 0:
            parameters = ', '.join(
                ['{option}={value}'.format(option=k,value=v) for k, v in self.options.items()])
            r = '{keyword} {parameters}'.format(keyword=self.name, parameters=parameters)
        return r


class Simple:
    storage_type = '' 

    def __init__(self, settings=None):
        self.settings = KeyValueOption('SETTINGS', **(settings or {}))

    def __str__(self):
        r = '{}()'.format(self.storage_type)
        r += ' {} '.format(self.settings)
        return r.strip()


class Memory(Simple):
    storage_type = 'Memory'


class Log(Simple):
    storage_type = 'Log'


class TinyLog(Simple):
    storage_type = 'TinyLog'


class StripeLog(Simple):
    storage_type = 'StripeLog'


class Set(Simple):
    storage_type = 'Set'


class GenericMergeTree:
    storage_type = 'MergeTree'

    def __init__(self, partition_by=None, order_by=None, sample_by=None, settings=None):
        self.partition_by = ListOption('PARTITION BY', *((partition_by) or ()))
        self.order_by = ListOption('ORDER BY', *((order_by) or ('tuple()',)))
        self.sample_by = ListOption('SAMPLE BY', *((sample_by) or ()))
        self.settings = KeyValueOption('SETTINGS', **(settings or {}))


class MergeTree(GenericMergeTree):
    storage_type = 'MergeTree'

    def __init__(self,
                 partition_by=None,
                 order_by=None,
                 primary_key=None,
                 sample_by=None,
                 ttl=None,
                 settings=None):
        self.primary_key = ListOption('PRIMARY KEY', *((primary_key) or ()))
        self.ttl = ListOption('TTL', *((ttl) or ()))
        super().__init__(
            partition_by=partition_by, order_by=order_by, sample_by=sample_by, settings=settings)

    def __str__(self):
        r = '{}()'.format(self.storage_type)
        r = (r + ' {}'.format(self.partition_by)).strip()
        r = (r + ' {}'.format(self.order_by)).strip()
        r = (r + ' {}'.format(self.primary_key)).strip()
        r = (r + ' {}'.format(self.sample_by)).strip()
        r = (r + ' {}'.format(self.ttl)).strip()
        r = (r + ' {}'.format(self.settings)).strip() 
        return r.strip()


class ReplacingMergeTree(GenericMergeTree):
    storage_type = 'ReplacingMergeTree'

    def __init__(self, 
                 partition_by=None,
                 order_by=None,
                 sample_by=None,
                 version=None,
                 settings=None):
        self.version = version
        super().__init__(
            partition_by=partition_by, order_by=order_by, sample_by=sample_by, settings=settings)

    def __str__(self):
        r = self.storage_type
        r += '({})'.format(self.version) if self.version else '()'
        r = (r + ' {}'.format(self.partition_by)).strip()
        r = (r + ' {}'.format(self.order_by)).strip()
        r = (r + ' {}'.format(self.sample_by)).strip()
        r = (r + ' {}'.format(self.settings)).strip()
        return r.strip()


class SummingMergeTree(GenericMergeTree):
    storage_type = 'SummingMergeTree'

    def __init__(self,
                 partition_by=None,
                 order_by=None,
                 sample_by=None,
                 columns=None,
                 settings=None):
        self.columns = columns
        super().__init__(
            partition_by=partition_by, order_by=order_by, sample_by=sample_by, settings=settings)

    def __str__(self):
        r = self.storage_type
        r += '({})'.format(self.columns) if self.columns else '()'
        r = (r + ' {}'.format(self.partition_by)).strip()
        r = (r + ' {}'.format(self.order_by)).strip()
        r = (r + ' {}'.format(self.sample_by)).strip()
        r = (r + ' {}'.format(self.settings)).strip()
        return r.strip()


class AggregatingMergeTree(GenericMergeTree):
    storage_type = 'AggregatingMergeTree'

    def __str__(self):
        r = self.storage_type
        r = (r + ' {}'.format(self.partition_by)).strip()
        r = (r + ' {}'.format(self.order_by)).strip()
        r = (r + ' {}'.format(self.sample_by)).strip()
        r = (r + ' {}'.format(self.settings)).strip()
        return r.strip()


class CollapsingMergeTree(GenericMergeTree):
    storage_type = 'CollapsingMergeTree'
    
    def __init__(self, partition_by=None, order_by=None, sample_by=None, sign=None, settings=None): 
        self.sign = sign
        super().__init__(
            partition_by=partition_by, order_by=order_by, sample_by=sample_by, settings=settings)

    def __str__(self):
        r = self.storage_type
        r += '({})'.format(self.sign) if self.sign else '()'
        r = (r + ' {}'.format(self.partition_by)).strip()
        r = (r + ' {}'.format(self.order_by)).strip()
        r = (r + ' {}'.format(self.sample_by)).strip()
        r = (r + ' {}'.format(self.settings)).strip()
        return r.strip()


class Join:
    def __init__(self, join_strictness, join_type, keys):
        self.join_strictness = join_strictness
        self.join_type = join_type
        self.keys = keys

    def __str__(self):
        r = 'Join({strictness}, {type}, {keys})'.format(
            strictness=self.join_strictness, type=self.join_type, keys=','.join(self.keys))
        return r
        

class BufferProfile:
    def __init__(self,
                 num_layers=16,
                 min_time=10,
                 max_time=100,
                 min_rows=10000,
                 max_rows=1000000,
                 min_bytes=10000000,
                 max_bytes=100000000,
                 prefix=None,
                 postfix=None):
        self.num_layers = num_layers
        self.min_time = min_time
        self.max_time = max_time
        self.min_rows = min_rows
        self.max_rows = max_rows
        self.min_bytes = min_bytes
        self.max_bytes = max_bytes
        self.prefix = prefix

    def DDL(self, database, table, prefix=None, postfix=None):
        buffer_table = table
        if prefix:
            buffer_table = '{}_{}'.format(prefix, buffer_table)
        if postfix:
            buffer_table = '{}_{}'.format(buffer_table, postfix)
        buffer_table_ddl = f'CREATE TABLE {database}.{buffer_table} AS {database}.{table} ENGINE = '
        buffer_profile = self.profile(database, table)
        return f'{buffer_table_ddl} {buffer_profile}'
    
    def profile(self, database, table):
        profile_options = ','.join(list(map(str, [database,
                                                  table,
                                                  self.num_layers,
                                                  self.min_time,
                                                  self.max_time,
                                                  self.min_rows,
                                                  self.max_rows,
                                                  self.min_bytes,
                                                  self.max_bytes])))
        return f'Buffer({profile_options})'
