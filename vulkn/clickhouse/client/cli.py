# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import itertools
import shlex
import logging
import subprocess


from vulkn.clickhouse.client.base import ClickHouseClient
from vulkn.clickhouse import sqlformat
from vulkn.config import FLAGS, SETTINGS, AUTH_OPTS, EXTERNAL_FILE_OPTS
from vulkn.recordset import RecordSet
from vulkn.utils import LogLevels


log = logging.getLogger()


CLI_FLAGS = [
    'disable_suggestion',
    'multiline',
    'multiquery',
    'testmode',
    'vertical',
    'time',
    'stacktrace',
    'progress',
    'echo'
]


CLI_OPTS = {
    'suggestion_limit': 10000
}


def flatten_args(d):
    return list(
        itertools.chain.from_iterable(
            [['--{}'.format(c), str(a)] for c, a in sorted(d.items())]))


def quote_shlex(cmd):
    return ' '.join([shlex.quote(c) for c in cmd])
    

class ClickHouseCLIClient(ClickHouseClient):
    def __init__(self, config_file=None, **kwargs):
        super(ClickHouseCLIClient, self).__init__(config_file, **kwargs)
    
    def _setFlags(self, **kwargs):
        self._flag_opts = filter(
            lambda k: k in set(FLAGS + CLI_FLAGS) and kwargs[k] == True,
            kwargs.keys())

    def _setOptions(self, **kwargs):
        self._opts = dict(
            filter(lambda k: k[0] in CLI_OPTS.keys(), kwargs.items()))

    def _setAuth(self, **kwargs):
        self._auth = dict(
            filter(lambda k: k[0] in AUTH_OPTS.keys(), kwargs.items()))

    def _setExternalFileOptions(self, **kwargs):
        self._external_file_opts = dict(
            filter(lambda k: k[0] in EXTERNAL_FILE_OPTS.keys(), kwargs.items()))

    def _setSettings(self, **kwargs):
        self._settings = dict(
            filter(lambda k: k[0] in SETTINGS, kwargs.items()))

    def _cli(self,
             config_file_overrides=None,
             flag_opts_overrides=None, 
             auth_overrides=None, 
             opts_overrides=None, 
             settings_overrides=None,
             external_file_overrides=None):
        config_file = config_file_overrides or self._config_file
        flag_opts = flag_opts_overrides or self._flag_opts
        opts = {**self._opts, **(opts_overrides or {})}
        auth_opts = {**self._auth, **(auth_overrides or {})}
        settings = {**self._settings, **(settings_overrides or {})}
        external_file_opts = {**self._external_file_opts,
                              **(external_file_overrides or {})}
        cmd = ['/usr/bin/clickhouse-client']
        if config_file:
            cmd += ['--config-file', config_file]
        if len(flag_opts) > 0:
            cmd += ['--{}'.format(c) for c in flag_opts]
        if len(auth_opts) > 0:
            cmd += flatten_args(auth_opts)
        if len(opts) > 0:
            cmd += flatten_args(opts)
        if len(settings) > 0:
            cmd += flatten_args(settings)
        if len(external_file_opts) > 0:
            cmd += flatten_args(external_file_opts)
        return cmd

    def _q(self, cli, query, settings=None):
        if cli is None:
            flag_opts_overrides = {'disable_suggestion': True}
            opts_overrides = {'format': 'TSVWithNamesAndTypes'}
            cli = self._cli(flag_opts_overrides=flag_opts_overrides,
                            opts_overrides=opts_overrides,
                            settings_overrides=settings)
        log.log(5, quote_shlex(cli))
        log.log(LogLevels.SQL, sqlformat(query))
        p = subprocess.run(cli,
                           input=query,
                           stdout=subprocess.PIPE,
                           universal_newlines=True)
        return p

    def execute(self, query, settings=None):
        q = self._q(None, query, settings=settings)
        return q.returncode

    def select(self, query, settings=None):
        flag_opts_overrides = {'disable_suggestion': True}
        opts_overrides = {'format': 'TSVWithNamesAndTypes'}
        cli = self._cli(flag_opts_overrides=flag_opts_overrides,
                        opts_overrides=opts_overrides,
                        settings_overrides=settings)
        q = self._q(cli, query, settings=settings)
        return RecordSet(q.stdout)
        
    def insert(self, query, settings=None):
        c = self._cli(settings=settings)

    def insert_blob(self, data, table, input_format='TSV', settings=None):
        flag_opts_overrides = {'disable_suggestion': True}
        opts_overrides = {'format': 'TSVWithNamesAndTypes'}
        cli = self._cli(flag_opts_overrides=flag_opts_overrides,
                        opts_overrides=opts_overrides,
                        settings_overrides=settings)
        cli += ['--query', 'INSERT INTO {} FORMAT {}'.format(table, input_format)]
        env = {'LC_ALL': 'C'}
        p = subprocess.run(cli, stdout=subprocess.PIPE, input=data, env=env, encoding='ascii')
        return p.returncode
