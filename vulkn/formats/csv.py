# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import copy
import csv
import subprocess
import logging


import vulkn
from vulkn.utils import LogLevels


log = logging.getLogger()


class CSV:
    CLICKHOUSE_FORMAT = 'CSV'

    OPTIONS = {
        'delimiter': ',',
        'allow_single_quotes': True,
        'allow_double_quotes': True,
        'unquoted_null_literal_is_null': True,
        'input_format_defaults_for_omitted_fields': False,
        'header': False,
        'infer_schema': False,
        'allow_enums': False,
        'column_format': 'snake_case',
        'overwrite': False,
        'engine': None,
        'sample_engine': None,
        'sample_size': 50000,
        'sample_preload': True,
        'schema': None}

    def __init__(self):
        self._options = copy.deepcopy(self.OPTIONS)

    def options(self, **kwargs):
        self._options.update(kwargs)
        return self

    def columns(self, uri):
        cols = []
        with open(uri.path, 'r') as f:
            reader = csv.reader(f)
            cols = next(reader)
        if not self._options['header']:
            cols = ['col{}'.format(i+1) for i, v in enumerate(cols)]
        return cols

    def sample(self, uri):
        lines = []
        i = 0
        with open(uri.path, 'r') as f:
            while True:
                if i == 0 and self._options['header']:
                    i = i+1
                    f.readline()
                    continue
                l = f.readline()
                if l == '' or i >= self._options['sample_size']:
                    break
                lines.append(l)
                i = i+1
        return ''.join(lines)

    def read(self, uri, database, table):
        # TODO: Next release. Hacky. Remove subprocess/cat pipeline.
        v = vulkn.Vulkn()
        header = 'CSVWithNames' if self._options['header'] else 'CSV'
        env = {'LC_ALL': 'C'}
        src = subprocess.Popen(['cat', uri.path], stdout=subprocess.PIPE, env=env, encoding='ascii')
        tgt = ['clickhouse-client', '-A', '-m', '-n']
        tgt += ['--host', v._host, '--port', str(v._port), '--user', v._user, '--password', v._password]
        tgt += ['--query', f'INSERT INTO {database}.{table} FORMAT {header}']
        log.debug(str(tgt))
        log.log(LogLevels.SQL, f'INSERT INTO {database}.{table} FORMAT {header}')
        p = subprocess.Popen(tgt, stdin=src.stdout, stdout=subprocess.PIPE, env=env, encoding='ascii')
        src.stdout.close()
        p.communicate()

    def write(self):
        pass

