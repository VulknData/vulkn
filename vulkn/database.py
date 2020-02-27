# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import ast
import logging


from vulkn.clickhouse import sqlformat
from vulkn.utils import timer


log = logging.getLogger()


class MutationManager:
    def __init__(self, ctx):
        self._ctx = ctx

    def _list(self):
        return self._ctx.q('SELECT * FROM system.mutations').exec()

    def show(self):
        self._list().show()

    def to_records(self):
        return self._list().to_records()

    def failed(self):
        return self._ctx.q("SELECT * FROM system.mutations WHERE latest_fail_reason != ''").exec()

    def kill(self, mutation_id):
        r = self._ctx.q(f"SELECT count() AS count FROM system.mutations WHERE mutation_id = '{mutation_id}'").exec().to_records()
        if r[0]['count'] == 0:
            raise Exception(f'Mutation {mutation_id} does not exist')
        return self._ctx.exec(f"KILL MUTATION WHERE mutation_id = '{mutation_id}'".format(mutation_id))

    def kill_all(self):
        return self._ctx.exec('KILL MUTATION WHERE 1 = 1')
    
    def active(self):
        return self._ctx.q("SELECT * FROM system.mutations WHERE is_done = 0").exec()


class VulknClickHouseDatabaseMixIn:
    def _set_db(self, table):
        if '.' not in table:
            table = '{database}.{table}'.format(database=self._database, table=table)
        return table

    def use(self, database):
        self._database = database
        self._conn = self._conn.setAuth(host=self._host,
                                        port=self._port,
                                        http_port=self._http_port,
                                        user=self._user,
                                        password=self._password,
                                        database=self._database)

    def desc(self, table):
        return self.q('DESC {}'.format(self._set_db(table))).exec()

    d = desc

    def get_create(self, table):
        return sqlformat(
            self.q('SHOW CREATE {}'.format(self._set_db(table))).e().to_records()[0]['statement'],
            oneline=False)

    getCreate = get_create

    def show_create(self, table):
        print(self.getCreate(table))

    showCreate = show_create

    c = showCreate

    def profile(self, table):
        def profile_column(table, column):
            column_type = column._col_type
            column_name = column._name
            profile_data = {}
            histogram = None
            profiles = []
            profile_data['uniq_values'] = (self.q(
                f'SELECT uniqCombined("{column_name}") AS uniq_values FROM {table}')
                .exec()
                .to_records())[0]['uniq_values']
            if profile_data['uniq_values'] <= 10:
                histogram = f"""
                    (SELECT
                        groupArray(({{subject}}, count))
                    FROM (
                        SELECT
                            {{subject}},
                            count() AS count
                        FROM {table}
                        GROUP BY {{subject}}
                        ORDER BY {{subject}}))"""
            else:
                histogram = f"""arrayMap(
                    x -> ({{subject_from}}(x.1), {{subject_from}}(x.2), round(x.3)),
                    histogram(10)({{subject_to}}))"""
            available_profiles = [
                "min({subject}) AS min",
                "max({subject}) AS max", 
                "mode",
                "countIf(isNull({subject})) AS nulls", 
                "count() AS total_records", 
                "toTypeName(any({subject})) AS data_type",
                "varSamp({subject_to}) AS var_samp",
                "varPop({subject_to}) AS var_pop",
                "stddevSamp({subject_to}) AS stddev_samp",
                "stddevPop({subject_to}) AS stddev_pop",
                "skewPop({subject_to}) AS skew_pop",
                "skewSamp({subject_to}) AS skew_samp",
                "kurtPop({subject_to}) AS kurt_pop",
                "kurtSamp({subject_to}) AS kurt_samp"
            ]
            if 'Date' in column_type:
                profiles.append(
                    "toDateTime(round(avg(toUInt32({subject})))) AS mean".format(subject=column_name))
                profiles.append(f"{histogram} AS histogram".format(subject=column_name,
                                                                   subject_to=f'toUInt32({column_name})',
                                                                   subject_from=f'toDateTime'))
                profiles.append("median({subject}) AS median".format(subject=column_name))
                for p in available_profiles:
                    profiles.append(p.format(subject=column_name,
                                             subject_to=f'toUInt32({column_name})',
                                             subject_from=f'toDateTime'))
            elif 'Int' in column_type:
                profiles.append(
                    "round(avg({subject})) AS mean".format(subject=column_name))
                profiles.append(f"{histogram} AS histogram".format(subject=column_name,
                                                                   subject_to=column_name,
                                                                   subject_from=''))
                profiles.append("median({subject}) AS median".format(subject=column_name))
                for p in available_profiles:
                    profiles.append(p.format(subject=column_name,
                                             subject_to=column_name,
                                             subject_from=f'round'))
            elif 'String' in column_type:
                profiles.append(
                    "round(avg(length({subject}))) AS mean_length".format(subject=column_name))
                profiles.append(
                    "round(min(length({subject}))) AS min_length".format(subject=column_name))
                profiles.append(
                    "round(max(length({subject}))) AS max_length".format(subject=column_name))
                profiles.append(
                    "round(median(length({subject}))) AS median_length".format(subject=column_name))
                for p in available_profiles:
                    profiles.append(p.format(subject=column_name,
                                             subject_to=f'length({column_name})',
                                             subject_from=f'round'))
            else:
                profiles.append("avg({subject}) AS mean".format(subject=column_name))
                profiles.append(f"{histogram} AS histogram".format(subject=column_name,
                                                                   subject_to=column_name,
                                                                   subject_from=''))
                profiles.append("median({subject}) AS median".format(subject=column_name))
                for p in available_profiles:
                    profiles.append(p.format(subject=column_name,
                                             subject_to=column_name,
                                             subject_from=''))
            profile_query = f"""
                WITH
                    (SELECT topK(10)({column_name}) FROM {table}) AS topK,
                    topK[1] AS mode
                SELECT
                    topK,
                    {','.join(profiles)}
                FROM {table}"""
            
            profile_data.update(self.q(profile_query).exec().to_records()[0])
            if 'histogram' in profile_data:
                profile_data['histogram'] = ast.literal_eval(profile_data['histogram'])
            if 'topK' in profile_data:
                profile_data['topK'] = ast.literal_eval(profile_data['topK'])
            return profile_data

        schema = self.getSchema(table)
        profiles = {}
        for column in schema:
            profiles[column._name] = profile_column(table, column)
        return profiles

    def get_schema(self, database=None, table=None):
        from vulkn.types import ColumnType
        schema = []
        if table is None and database is not None:
            table = database
            database = None
        if table is None:
            raise Exception('No table specified')
        if database is None:
            database = self._database
        sql = """
            SELECT
                name,
                type,
                default_kind,
                default_expression,
                compression_codec
            FROM system.columns 
            WHERE database = {database:String} AND table = {table:String}"""
        columns = self.q(sql).exec(database=database, table=table).to_records()
        for r in columns:
            schema.append(
                ColumnType(r['name'],
                          r['type'],
                          default_kind=r['default_kind'],
                          default_expression=r['default_expression'],
                          compression_codec=r['compression_codec']))
        return schema

    getSchema = get_schema
    schema = get_schema

    def db(self):
        return self.q('SHOW DATABASES').exec()

    def tables(self, database=None):
        if database is None:
            database = self._database
        return self.q("""
            SELECT database, name, engine, partition_key, sorting_key
            FROM system.tables
            WHERE database = {database:String}
            ORDER BY database != 'system' DESC, database,  engine, name""").exec(database=database)

    t = tables
    
    def optimize(self, database, table, partition=None, final=False, deduplicate=False):
        ddl = f'OPTIMIZE TABLE {database}.{table}'
        if final:
            ddl += ' FINAL'
        if deduplicate:
            ddl += ' DEDUPLICATE'
        return self.exec(ddl)

    def parts(self, database=None, table=None):
        if table is None and database is not None:
            table = database
            database = None
        if table is None:
            raise Exception('No table specified')
        if database is None:
            database = self._database
        return self.q("""
            SELECT partition, rows, path
            FROM system.parts
            WHERE
                active
                AND (
                    (database = {database:String} AND table = {table:String}) 
                    OR database || '.' || table = {table:String})
            ORDER BY partition""").exec(database=database, table=table)

    def drop_part(self, database=None, table=None, partitions=None):
        if partitions is None and database is not None and table is not None:
            partitions = table
            table = database
            database = self._database
        if ((partitions is None or database is None or table is None) 
                or not isinstance(partitions, list)):
            raise Exception('Invalid parameters passed to dropPart')
        ddl = f'ALTER TABLE {database}.{table} DROP PARTITION '
        for p in partitions:
            if not self.exec("{} '{}'".format(ddl, p)):
                raise Exception(f'Unable to drop partition {p}')
        return True

    dropPart = drop_part

    def clone_table(self, from_database, from_table, database, table):
        ddl = f'CREATE TABLE {database}.{table} AS {from_database}.{from_table}'
        return self.exec(ddl)

    cloneTable = clone_table

    def copy_table(self, from_database, from_table, database, table):
        if not self.cloneTable(from_database, from_table, database, table):
            raise Exception('Unable to clone table')
        return self.exec(f'INSERT INTO {database}.{table} SELECT * FROM {from_database}.{from_table}')

    copyTable = copy_table

    def create_table(self, database=None, table=None, schema=None, engine=None, exists_ok=False):
        schema_ddl = ', '.join(['{} {}'.format(k, v) for k, v in schema.items()])
        ddl = f'CREATE TABLE {database}.{table} ({schema_ddl}) ENGINE = {engine}'
        return self.exec(ddl)

    createTable = create_table

    def create_sink(self, database, sink, schema, exists_ok=False):
        schema_ddl = ', '.join(['{} {}'.format(k, v) for k, v in schema.items()])
        ddl = f'CREATE TABLE {database}.{sink} ({schema_ddl}) ENGINE = Null'
        return self.exec(ddl)

    createSink = create_sink

    def create_view(self, database, view, query, exists_ok=False):
        ddl = f'CREATE VIEW {database}.{view} AS {query}'
        return self.exec(ddl)

    createView = create_view

    def create_mat_view(self,
                      database,
                      view,
                      query,
                      to_database=None,
                      to_table=None,
                      engine=None,
                      exists_ok=False):
        ddl = f'CREATE MATERIALIZED VIEW {database}.{view} '
        if to_database is not None and to_table is not None:
            ddl = f'TO {to_database}.{to_table} AS {query}'
        else:
            engine = engine or engines.MergeTree()
            ddl = f'ENGINE = {engine} AS {query}'
        return self.exec(ddl)

    createMatView = create_mat_view

    def drop_table(self, database, table):
        ddl = f'DROP TABLE IF EXISTS {database}.{table}'
        return self.exec(ddl)

    dropTable = drop_table

    def drop_columns(self, database, table, columns):
        r = True
        for c in columns:
            try:
                if not self.exec(f'ALTER TABLE {database}.{table} DROP COLUMN {c}'):
                    r = False
                    log.info(f'Unable to drop column {c} on {database}.{table}')
            except:
                r = False
                log.info(f'Unable to drop column {c} on {database}.{table}')
        return r

    def truncate_table(self, database, table):
        ddl = f'TRUNCATE TABLE {database}.{table}'
        return self.exec(ddl)

    truncateTable = truncate_table

    def table_exists(self, database, table):
        exists = f"""
            SELECT count()>0 AS exists 
            FROM system.tables
            WHERE (name = '{table}') OR concat(database, '.', name) = '{database}.{table}'"""
        return self.q(exists).exec().to_records()[0]['exists'] == 1

    tableExists = table_exists

    dropSink = drop_table
    drop_sink = drop_table
    dropView = drop_table
    drop_view = drop_table
    dropMatView = drop_table
    drop_mat_view = drop_table

    @timer
    def exec(self, query, settings=None):
        try:
            r = self._conn.execute(query)
            return True
        except:
            return False

    e = exec


class VulknSystemManager:
    def __init__(self, ctx):
        self._ctx = ctx
        self.exec = self._ctx.exec

    def reload_dicts(self):
        return self.exec('SYSTEM RELOAD DICTIONARIES')

    def reload_dict(self, dictionary):
        return self.exec(f'SYSTEM RELOAD DICTIONARY {dictionary}')

    def drop_dns_cache(self):
        return self.exec('SYSTEM DROP DNS CACHE')

    def drop_mark_cache(self):
        return self.exec('SYSTEM DROP MARK CACHE')

    def flush_logs(self):
        return self.exec('SYSTEM FLUSH LOGS')

    def reload_config(self):
        return self.exec('SYSTEM RELOAD CONFIG')

    def shutdown(self):
        return self.exec('SYSTEM SHUTDOWN')

    def kill(self):
        return self.exec('SYSTEM KILL')

    def stop_dist_sends(self, database, table):
        return self.exec(f'SYSTEM STOP DISTRIBUTED SENDS {database}.{table}')

    def flush_dist(self, database, table):
        return self.exec(f'SYSTEM FLUSH {database}.{table}')

    def start_dist_sends(self, database, table):
        return self.exec(f'SYSTEM START DISTRIBUTED SENDS {database}.{table}')

    def stop_merges(self, database, table):
        return self.exec(f'SYSTEM STOP MERGES {database}.{table}')

    def start_merges(self, database, table):
        return self.exec(f'SYSTEM START MERGES {database}.{table}')
