# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import logging


import vulkn.sql
import vulkn.table
import vulkn.reader
import vulkn.dataframe
from vulkn.utils import singleton
from vulkn.catalog import VulknCatalogViewer
from vulkn.data import VulknDataStore
from vulkn.session import VulknSession
from vulkn.database import VulknClickHouseDatabaseMixIn, MutationManager
from vulkn.scheduler import VulknScheduler
from vulkn.clickhouse.client.cli import ClickHouseCLIClient


log = logging.getLogger()


class VulknDataFramesMixIn:
    def q(self, query):
        return vulkn.dataframe.QueryStringDataFrame(self, query)

    def select(self, *cols):
        return vulkn.dataframe.SelectQueryDataFrame(self).select(*cols)

    def s(self, *cols):
        r = self.select(*cols).exec().to_records()
        if len(r) == 1:
            return list(r[0].values())[0]
        else:
            return r

    def numbers(self, count, system=False, mt=False):
        return vulkn.dataframe.NumbersDataFrame(self, count, system, mt)

    def range(self, start, end, system=False, mt=False):
        return vulkn.dataframe.RangeDataFrame(self, start, end, system, mt)

    def one(self):
        return vulkn.dataframe.OneDataFrame(self)

    def random(self, count, start=0, end=18446744073709551615, system=False, mt=False):
        return vulkn.dataframe.RandomDataFrame(self, count, start, end, system, mt)

    def randfloat(self, count, start=0, end=18446744073709551615, system=False, mt=False):
        return vulkn.dataframe.RandomFloatDataFrame(self, count, start, end, system, mt)
    
    def with_(self, *cols):
        return vulkn.dataframe.SelectQueryDataFrame(self).with_(*cols)

    def update(self, table):
        return vulkn.dataframe.UpdateQueryDataFrame(self, table)

    def delete(self, table):
        return vulkn.dataframe.DeleteQueryDataFrame(self, table)


@singleton
class Vulkn(VulknDataFramesMixIn, VulknClickHouseDatabaseMixIn):
    def __init__(self,
                 user='default',
                 password='',
                 host='localhost',
                 port=9000,
                 database='default',
                 workspace=None):
        if workspace is not None:
            port = workspace._port
            http_port = workspace._http_port
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self._database = database
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
        self.sys = self.system

    def _reload(self):
        if self.session:
            self.session.destroySession()
            del self.session
        self._conn = self._reload_conn()
        self.session = VulknSession(self)

    def _reload_conn(self):
        return ClickHouseCLIClient().setAuth(host=self._host,
                                             port=self._port,
                                             user=self._user,
                                             password=self._password,
                                             database=self._database)

