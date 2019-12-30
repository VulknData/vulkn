# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


class VulknCatalogViewer:
    def __init__(self, ctx, catalog='system', hidden=None):
        self._ctx = ctx
        self._catalog = catalog
        self._hidden = hidden or []

    def __getattr__(self, attrname):
        if attrname in self._hidden:
            raise AttributeError
        sql = "SELECT name FROM system.tables WHERE name = {name:String} AND database = {catalog:String}"
        t = self._ctx.q(sql).exec(catalog=self._catalog, name=attrname).to_records()
        if len(t) > 0:
            return self._ctx.q(f'SELECT * FROM "{self._catalog}"."{attrname}"').exec()
        else:
            raise AttributeError

    def help(self):
        sql = "SELECT name FROM system.tables WHERE database = {catalog:String} ORDER BY name"
        return [n['name'] for n in self._ctx.q(sql).exec(catalog=self._catalog).to_records()]


class VulknCatalog:
    def __init__(self, ctx):
        self._ctx = ctx

    @property
    def h(self):
        print('\n'.join([
            'tables', 'table_engines', 'mutations']))

    @property
    def tables(self):
        return self._ctx.q("""
            SELECT
                database, name, engine, partition_key, sorting_key
            FROM system.tables
            ORDER BY 
                database != 'system' DESC,
                database, 
                engine,
                name""").s

    @property
    def table_engines(self):
        return self._ctx.q("""
            SELECT
                name
            FROM system.table_engines
            ORDER BY
                name LIKE '%MergeTree%',
                name LIKE '%Replicated%', 
                name""").s

    @property
    def mutations(self):
        return self._ctx.q("""
            select 
                create_time, database || '.' || table as table, command, parts_to_do, is_done, 
                latest_failed_part, latest_fail_time, latest_fail_reason
            from system.mutations order by table""").s

    @property
    def databases(self):
        return self._ctx.q("select * from system.databases").s

    @property
    def settings(self):
        return self._ctx.q("SELECT name, value FROM system.settings ORDER BY name").s

    @property
    def functions(self):
        return self._ctx.q("select name from system.functions where is_aggregate = 0 order by name").s

    @property
    def aggfunctions(self):
        return self._ctx.q("select name from system.functions where is_aggregate = 1 order by name").s

    @property
    def clusters(self):
        return self._ctx.q('select * from system.clusters order by cluster').s

    @property
    def formats(self):
        return self._ctx.q('select * from system.formats order by name').s

    @property
    def parts(self):
        return self._ctx.q('select * from system.parts order by database, table').s

    @property
    def metrics(self):
        return self._ctx.q('select * from system.metrics order by metric').s

    @property
    def merge_tree_settings(self):
        return self._ctx.q('select * from system.merge_tree_settings order by name').s

    @property
    def events(self):
        return self._ctx.q('select * from system.events order by event').s

    @property
    def dicts(self):
        return self._ctx.q('select * from system.dictionaries').s

    @property
    def datatypes(self):
        return self._ctx.q('select * from system.data_type_families').s

    @property
    def build_options(self):
        return self._ctx.q('select * from system.build_options').s

    @property
    def columns(self):
        return self._ctx.q('select * from system.columns order by database, table, name').s