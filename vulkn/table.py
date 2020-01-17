# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import vulkn.engines
from vulkn.datatable import BaseTableDataTable
from vulkn.utils import timer


class Table:
    def __new__(self, database, table=None):
        import vulkn
        ctx = vulkn.Vulkn()
        if table is None:
            if '.' in database:
                database, table = database.split('.')
            else:
                table = database
                database = None
            database = database or ctx._database
        return BaseTableDataTable(ctx, database, table)

    @classmethod
    @timer
    def fromVector(self, name, columns=(), engine=None, buffer_profile=None, replace=False):
        import vulkn
        database = ''
        table = ''
        ctx = vulkn.Vulkn()
        if isinstance(name, tuple):
            (database, table) = (name[0], name[1])
        if isinstance(name, str):
            (database, table) = name.split('.')
        engine = engine or vulkn.engines.Memory()
        if replace:
            ctx._conn.execute(f'DROP TABLE IF EXISTS {database}.{table}')
        ddl = Table.DDL(database, table, columns, engine, buffer_profile)
        for ddl_query in ddl:
            ctx._conn.execute(ddl_query)
        return BaseTableDataTable(ctx, database, table)

    @staticmethod
    def column_list(columns):
        # TODO: Next release. Whole thing is hacky. Needs refactoring.
        from vulkn.types import ArrayVector, ColumnVector
        from vulkn import Vulkn
        ctx = vulkn.Vulkn()
        rangeCols = []
        selectExprList = []
        q = None
        for idx, column in enumerate(columns):
            if isinstance(column, ArrayVector):
                if hasattr(column, 'vector_name'):
                    selectExprList.append(
                        'v.{index} AS {name}'.format(index=str(idx+1), name=column.vector_name))
                else:
                    selectExprList.append(
                        'v.{index} AS col{index}'.format(index=str(idx+1)))
                rangeCols.append("joinGet('{table}', 'v', 1)".format(table=str(column._cache_table)))
            if isinstance(column, ColumnVector):
                if hasattr(column, 'vector_name'):
                    selectExprList.append(
                        'c{index}.v AS {name}'.format(index=str(idx), name=column.vector_name))
                else:    
                    selectExprList.append(
                        'c{index}.v AS col{index}'.format(index=str(idx)))
                if idx == 0:
                    rangeCols.append('FROM ({}) c0'.format(str(column)))
                else:
                    rangeCols.append(
                        'ANY LEFT JOIN ({subquery}) c{index} ON (c{prevIndex}.i = c{index}.i)'.format(
                            subquery=str(column), index=str(idx), prevIndex=str(idx-1)))
        if isinstance(column, ArrayVector):
            arrayCols = [f'v{i+1}' for i,k in enumerate(rangeCols)]
            ctx.session.optimize(final=True)
            q = """WITH
                    arrayJoin(
                        arrayMap(
                            ({array_cols}) -> ({array_cols}),
                            {source_cols})) AS v
                SELECT {columns}""".format(array_cols=','.join(arrayCols),
                                           source_cols=',\n'.join(rangeCols),
                                           columns=', '.join(selectExprList),
                                           session_cache=ctx.session.session_store)
        if isinstance(column, ColumnVector):
            q = "SELECT {selectExpr} {rangeCols}".format(selectExpr=', '.join(selectExprList),
                                                         rangeCols=' '.join(rangeCols))
        return q

    @staticmethod
    def DDL(database, table, columns, engine, buffer_profile):
        columns = Table.column_list(columns)
        engine = str(engine)
        r = [f'CREATE TABLE {database}.{table} ENGINE = {engine} AS {columns}']
        if buffer_profile:
            r.append(buffer_profile.DDL(database, table))
        return r


table = Table
