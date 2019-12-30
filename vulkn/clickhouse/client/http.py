# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from requests import HTTPSession


from vulkn.clickhouse.client.base import ClickHouseClient


class ClickHouseHTTPClient(ClickHouseClient):
    def __init__(self, config_file: str=None, **kwargs: dict) -> None:
        super(ClickHouseHTTPClient, self).__init__(config_file, **kwargs)      
        self._http = HTTPSession()  

    def _q(self, query: str, settings: dict=None) -> dict:
        r = http.request('get', self._host, self._port)

    def select(self, query: str, settings: dict=None) -> None:
        return self._q(query)