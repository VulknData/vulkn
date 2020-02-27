# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import urllib3
import logging


from vulkn.clickhouse.client.base import ClickHouseClient
from vulkn.clickhouse import sqlformat
from vulkn.config import FLAGS, SETTINGS, AUTH_OPTS, EXTERNAL_FILE_OPTS
from vulkn.recordset import RecordSet
from vulkn.utils import LogLevels


log = logging.getLogger()


class ClickHouseHTTPClient(ClickHouseClient):
    def __init__(self, config_file: str=None, **kwargs: dict) -> None:
        super(ClickHouseHTTPClient, self).__init__(config_file, **kwargs)      
        self._http = urllib3.PoolManager(cert_reqs='CERT_NONE')

    def _q(self, query: str, settings: dict=None) -> dict:
        host = self._auth.get('host')
        if not host.startswith('http'):
            host = f'http://{host}'
        port = self._auth.get('http_port')
        log.log(LogLevels.SQL, sqlformat(query))
        headers = {
            'X-ClickHouse-User': self._auth.get('user'),
            'X-ClickHouse-Key': self._auth.get('password')}
        body = f'{query}'
        if (query.strip().lower().startswith('select') or 
                query.strip().lower().startswith('with') or
                query.strip().lower().startswith('show')):
            body = f'{body} FORMAT TSVWithNamesAndTypes'
        s = '' if not settings else '&'.join([f'{k}={i}'.format(k, i) for k, i in settings.items()])
        if s != '':
            log.log(LogLevels.SQL, s)
        r = self._http.request('POST', f'{host}:{port}/?{s}', headers=headers, body=body)
        return r

    def execute(self, query, settings=None):
        q = self._q(query, settings=settings)
        return q.status == 200

    def select(self, query: str, settings: dict=None) -> None:
        q = self._q(query, settings=settings)
        if q.status != 200:
            raise Exception(q.data.decode('UTF8'))
        return RecordSet(q.data.decode('UTF8'))

    def _setFlags(self, **kwargs: dict):
        pass

    def _setOptions(self, **kwargs: dict):
        pass

    def _setAuth(self, **kwargs: dict):
        self._auth = dict(filter(lambda k: k[0] in AUTH_OPTS.keys(), kwargs.items()))
        self._auth['http_port'] = kwargs.get('http_port')

    def _setExternalFileOptions(self, **kwargs: dict):
        pass

    def _setSettings(self, **kwargs: dict):
        pass
    
