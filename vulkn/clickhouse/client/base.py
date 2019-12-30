# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import logging


from vulkn.config import FLAGS, SETTINGS, AUTH_OPTS, EXTERNAL_FILE_OPTS
from vulkn.recordset import RecordSet


log = logging.getLogger()


class ClickHouseClient:
    def __init__(self, config_file: str=None, **kwargs: dict) -> None:
        self._config_file = config_file
        self.setFlags(**kwargs)
        self.setOptions(**kwargs)
        self.setAuth(**kwargs)
        self.setExternalFileOptions(**kwargs)
        self._setSettings(**kwargs)

    def setFlags(self, **kwargs: dict) -> any:
        self._setFlags(**kwargs)
        return self

    def setOptions(self, **kwargs: dict) -> any:
        self._setOptions(**kwargs)
        return self

    def setAuth(self, **kwargs: dict) -> any:
        self._setAuth(**kwargs)
        return self

    def setExternalFileOptions(self, **kwargs: dict) -> any:
        self._setExternalFileOptions(**kwargs)
        return self

    def settings(self, **kwargs: dict) -> any:
        self._setSettings(**kwargs)
        return self

    def _q(self, query: str, settings: dict=None) -> any:
        pass

    def execute(self, query: str, settings: dict=None) -> any:
        q = self._q(query, settings=settings)
        return q.returncode

    def select(self, query: str, settings: dict=None) -> RecordSet:
        q = self._q(query, settings=settings)
        return RecordSet(q.stdout)
        
    def insert(self, query: str, settings: dict=None) -> None:
        c = self._cli(settings=settings)

    def insert_blob(self, query: str, input_format: str='TSV', settings: dict=None) -> None:
        c = self._cli(settings=settings)
        c += ['--query', '{} FORMAT {}'.format(query, input_format)]

