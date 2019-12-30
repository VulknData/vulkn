# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


class ClickHouseCLIWriter:
    OPTIONS = { 'options': {}, 'client': None, 'format': None}

    def __init__(self):
        self._options = copy.deepcopy(self.OPTIONS)

    def options(self, **kwargs):
        self._options.update(kwargs)
        return self

    def _cli(self, database, table):
        flag_opts_overrides = {'disable_suggestion': True}
        opts_overrides = {'format': self._options['format'] or 'CSV'}
        cli = self._cli(flag_opts_overrides=flag_opts_overrides,
                        opts_overrides=opts_overrides,
                        settings_overrides=settings)
        cli += ['--query', 'INSERT INTO {}.{} FORMAT {}'.format(database, table, input_format)]
        env = {'LC_ALL': 'C'}
        return cli
        
    def write(self, source, database, table):
        target = self._cli(database, table)
        p = subprocess.run(
            cli, stdout=subprocess.PIPE, input=source.buffer(), env=env, encoding='ascii')
        return p.returncode