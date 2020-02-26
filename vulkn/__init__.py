# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import ast
import logging
import sys


import vulkn.sql
import vulkn.table
import vulkn.reader
import vulkn.datatable
from vulkn.utils import singleton
from vulkn.catalog import VulknCatalogViewer
from vulkn.data import VulknDataStore
from vulkn.session import VulknSession
from vulkn.database import VulknClickHouseDatabaseMixIn, MutationManager, VulknSystemManager
from vulkn.scheduler import VulknScheduler
from vulkn.clickhouse.client.http import ClickHouseHTTPClient
from vulkn.clickhouse.client.cli import ClickHouseCLIClient

log = logging.getLogger()


class VulknDataTablesMixIn:
    def q(self, query):
        return vulkn.datatable.QueryStringDataTable(self, query)

    def select(self, *cols):
        return vulkn.datatable.SelectQueryDataTable(self).select(*cols)

    def s(self, *cols):
        r = self.select(*cols).exec().to_list()
        if len(r) > 0:
            try:
                return ast.literal_eval(r[0] if len(r[0]) > 1 else r[0][0])
            except:
                return r[0] if len(r[0]) > 1 else r[0][0]
        return None

    def numbers(self, count, system=False, mt=False):
        return vulkn.datatable.NumbersDataTable(self, count, system, mt)

    def range(self, start, end, system=False, mt=False):
        return vulkn.datatable.RangeDataTable(self, start, end, system, mt)

    def one(self):
        return vulkn.datatable.OneDataTable(self)

    def random(self, count, start=0, end=((sys.maxsize*2)+1), system=False, mt=False):
        return vulkn.datatable.RandomDataTable(self, count, start, end, system, mt)

    def randfloat(self, count, start=0, end=((sys.maxsize*2)+1), system=False, mt=False):
        return vulkn.datatable.RandomFloatDataTable(self, count, start, end, system, mt)
    
    def with_(self, *cols):
        return vulkn.datatable.SelectQueryDataTable(self).with_(*cols)

    def update(self, table):
        return vulkn.datatable.UpdateQueryDataTable(self, table)

    def delete(self, table):
        return vulkn.datatable.DeleteQueryDataTable(self, table)


@singleton
class Vulkn(VulknDataTablesMixIn, VulknClickHouseDatabaseMixIn):
    def __init__(self,
                 user='default',
                 password='',
                 host='localhost',
                 port=9000,
                 http_port=8123,
                 database='default',
                 workspace=None,
                 client='cli'):
        if workspace is not None:
            port = workspace._port
            http_port = workspace._http_port
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self._http_port = http_port
        self._database = database
        self._client = client
        self._conn = self._reload_conn()
        self.session = None
        self.scheduler = VulknScheduler(self)
        self.session = VulknSession(self)
        self.mutations = MutationManager(self)
        self.read = vulkn.reader.Reader()
        self.table = vulkn.table.Table
        self.system = VulknCatalogViewer(self,
                                         catalog='system',
                                         hidden=['numbers','numbers_mt','one','zero','zero_mt'])
        self.data = VulknDataStore(self)
        self.sys = VulknSystemManager(self)

    def _reload(self):
        if self.session:
            self.session.destroySession()
            del self.session
        self._conn = self._reload_conn()
        self.session = VulknSession(self)

    def _reload_conn(self):
        ClientFactory = { 'cli': ClickHouseCLIClient, 'http': ClickHouseHTTPClient }
        return (ClientFactory[self._client]()
            .setAuth(host=self._host,
                     port=self._port,
                     http_port=self._http_port,     
                     user=self._user,
                     password=self._password,
                     database=self._database))
