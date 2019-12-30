# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from vulkn.clickhouse.client.cli import ClickHouseCLIClient
from vulkn.clickhouse.client.http import ClickHouseHTTPClient
   

class ClickHouseHybridClient():
    def __init__(self, config_file=None, **kwargs):
        self._cli = ClickHouseCLIClient(config_file, **kwargs)
        self._http = ClickHouseHTTPClient(config_file, **kwargs)
    
    def _q(self, query, settings=None):
        pass

    def execute(self, query, settings=None):
        q = self._q(query, settings=settings)
        return q.returncode

    def select(self, query, settings=None):
        q = self._q(query, settings=settings)
        return RecordSet(q.stdout)
        
    def insert(self, query, settings=None):
        pass

    def insert_blob(self, query, input_format='TSV', settings=None):
        pass

    def create_database(self, database):
        return self.execute(
            'CREATE DATABASE IF NOT EXISTS {database}'.format(database=database))

    def drop_table(self, database, table):
        return self.execute(
            'DROP TABLE IF EXISTS {database}.{table}'.format(database=database, 
                                                             table=table))

    def drop_database(self, database):
        return self.execute(
            'DROP DATABASE IF EXISTS {database}'.format(database=database))

    def drop_view(self, database, view):
        self.drop_table(database, view)

    def fetch_scalar(self, query, column):
        return self.select(query)[0][column]

    def check_bool(self, query, column):
        return int(self.fetch_scalar(query, column)) == 1

    def table_exists(self, database, table):
        return self.check_bool(
            'EXISTS TABLE {database}.{table}'.format(database=database,
                                                     table=table),
            'result')

    def view_exists(self, database, view):
        return self.check_bool("""
            SELECT
                count()>0 AS result
            FROM system.tables
            WHERE 
                database = '{database}' 
                AND name = '{view}' 
                AND engine = 'View'""".format(database=database, view=view),
            'result')

    def database_exists(self, database):
        return self.check_bool("""
            SELECT
                count()>0 AS result
            FROM system.databases
            WHERE name = '{database}'""".format(database=database),
            'result')
    
    def detach_table(self, database, table):
        self.execute('DETACH TABLE {database}.{table}'.format(
            database=database, table=table))

    def list_databases(self):
        return [r['name'] for r in self.select('SHOW DATABASES')]

    def list_tables(self, database):
        return [r['name'] for r in self.select("""
            SELECT
                name
            FROM system.tables
            WHERE create_table_query LIKE 'CREATE TABLE%'
                AND database = '{database}'
            ORDER BY name""".format(database=database))]

    def list_views(self, database):
        return [r['name'] for r in self.select("""
            SELECT
                name
            FROM system.tables
            WHERE engine = 'View' AND database = '{database}'
            ORDER BY name""".format(database=database))]
