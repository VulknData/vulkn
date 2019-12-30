# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from collections.abc import Mapping


class VulknDataStore(Mapping):
    def __init__(self, ctx, root=None):
        self._ctx = ctx
        self._root = root

    def __getattr__(self, attrname):
        if not self._root:
            sql = "SELECT name FROM system.databases WHERE name = {catalog:String}"
            t = self._ctx.q(sql).exec(catalog=attrname).to_records()
            if len(t) > 0:
                return VulknDataStore(ctx=self._ctx, root=t[0]['name'])
        else:
            sql = "SELECT name FROM system.tables WHERE database = {catalog:String} AND name = {table:String}"
            t = self._ctx.q(sql).exec(catalog=self._root, table=attrname).to_records()
            if len(t) > 0:
                return self._ctx.table(f'{self._root}.{attrname}')
            raise AttributeError

    def __getitem__(self, key):
        sql = "SELECT database, name FROM system.tables WHERE (database || '.' || name) = {key:String}"
        t = self._ctx.q(sql).exec(key=key).to_records()
        if len(t) > 0:
            return self._ctx.table(t[0]['database'], t[0]['name'])
        raise AttributeError

    def __iter__(self):
        sql = "SELECT database, name FROM system.tables ORDER BY database, name"
        d = {}
        for r in self._ctx.q(sql).exec().to_records():
            database = r['database']
            table = r['name']
            d[f'{database}.{table}'] = self._ctx.table(database, table)
        return iter(d)

    def __len__(self):
        sql = "SELECT count() AS count FROM system.tables"
        t = int(self._ctx.q(sql).exec().to_records()[0]['count'])
        return t

    def help(self):
        sql = "SELECT name FROM system.tables WHERE database = {catalog:String} ORDER BY name"
        return [n['name'] for n in self._ctx.q(sql).exec(catalog=self._catalog).to_records()]

