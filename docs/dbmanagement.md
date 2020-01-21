# Object Management & Profiling

Vulkn provides some simple functions for managing and interrogating objects. These range from simple
CRUD operations to partition management and data profiling.
---

## Data Profiling

### *v.profile(table: str)*

* Description: Profiles the table returning statistical information regarding the shape of the data. Data types are inspected using different methods or options such as max_length for character types vs max values for decimals.
* Parameters
    * ```table``` - the table to inspect
* Returns
    * ```dict```
* Example
    ```python
    >>> v.profile('timeseries')
    {'key': {'data_type': 'String',
            'kurt_pop': 13.22782691569896,
            'kurt_samp': 13.227785078755689,
            'max': 'device-999',
            'max_length': 10,
            'mean_length': 10,
            'median_length': 10,
            'min': 'device-0',
            'min_length': 8,
            'mode': 'device-990',
            'nulls': 0,
            'skew_pop': -3.2023548144821627,
            'skew_samp': -3.2023472181783337,
            'stddev_pop': 0.34284272666371696,
            'stddev_samp': 0.34284299774981736,
            'topK': ['device-990',
                    'device-984',
                    'device-851',
                    'device-878',
                    'device-991',
                    'device-849',
                    'device-934',
                    'device-828',
                    'device-839',
                    'device-362'],
            'total_records': 632351,
            'uniq_values': 1000,
            'var_pop': 0.11754113522621215,
            'var_samp': 0.11754132110608125},
    'ts': {'data_type': "DateTime(\\'Australia/Melbourne\\')",
            'histogram': [('2019-01-01 00:00:00', '2019-01-01 00:01:35', 59936),
                        ('2019-01-01 00:01:35', '2019-01-01 00:03:09', 59411),
                        ('2019-01-01 00:03:09', '2019-01-01 00:04:45', 60835),
                        ('2019-01-01 00:04:45', '2019-01-01 00:06:24', 63316),
                        ('2019-01-01 00:06:24', '2019-01-01 00:08:07', 64741),
                        ('2019-01-01 00:08:07', '2019-01-01 00:09:51', 65790),
                        ('2019-01-01 00:09:51', '2019-01-01 00:11:37', 67164),
                        ('2019-01-01 00:11:37', '2019-01-01 00:13:22', 66577),
                        ('2019-01-01 00:13:22', '2019-01-01 00:15:02', 63605),
                        ('2019-01-01 00:15:02', '2019-01-01 00:16:39', 60975)],
            'kurt_pop': -251816852146683.28,
            'kurt_samp': -251816055700870.62,
            'max': '2019-01-01 00:16:39',
            'mean': '2019-01-01 00:08:20',
            'median': '2019-01-01 00:08:16',
            'min': '2019-01-01 00:00:00',
            'mode': '2019-01-01 00:16:38',
            'nulls': 0,
            'skew_pop': 16028484.98636335,
            'skew_samp': 16028446.965204256,
            'stddev_pop': 231.27362468169503,
            'stddev_samp': 231.2738075499905,
            'topK': ['2019-01-01 00:16:38',
                    '2019-01-01 00:15:48',
                    '2019-01-01 00:15:55',
                    '2019-01-01 00:16:06',
                    '2019-01-01 00:16:09',
                    '2019-01-01 00:16:15',
                    '2019-01-01 00:16:18',
                    '2019-01-01 00:16:19',
                    '2019-01-01 00:16:20',
                    '2019-01-01 00:16:23'],
            'total_records': 632351,
            'uniq_values': 1000,
            'var_pop': 53487.48947340954,
            'var_samp': 53487.57405867004},
    'value': {'data_type': 'UInt32',
            'histogram': [(246, 454075146.24017453, 66170),
                            (454075146.24017453, 902366140.8160808, 65836),
                            (902366140.8160808, 1310216847.6019177, 62907),
                            (1310216847.6019177, 1674819224.429403, 50024),
                            (1674819224.429403, 2067148057.3543935, 60125),
                            (2067148057.3543935, 2492222219.7494526, 61820),
                            (2492222219.7494526, 2922957520.3494115, 62958),
                            (2922957520.3494115, 3366978285.4684887, 65516),
                            (3366978285.4684887, 3825636033.0746126, 67631),
                            (3825636033.0746126, 4294934229, 69363)],
            'kurt_pop': 1.8003812394411711,
            'kurt_samp': 1.8003755451991572,
            'max': 4294934229,
            'mean': 2148598926,
            'median': 2178824636,
            'min': 246,
            'mode': 1290303696,
            'nulls': 0,
            'skew_pop': -0.0002275688367801933,
            'skew_samp': -0.0002275682969642996,
            'stddev_pop': 1239547006.8484387,
            'stddev_samp': 1239547986.9595456,
            'topK': [1290303696,
                        2903569362,
                        2615129534,
                        33938448,
                        4286069806,
                        586779699,
                        662198152,
                        2473897446,
                        2284234981,
                        1655328950],
            'total_records': 632351,
            'uniq_values': 632339,
            'var_pop': 1536476782186923500,
            'var_samp': 1536479211975462000}}
    ```
---

## Management Operations

### *v.use(database: str)*

* Description: Sets the current table search path to the named database.
* Parameters
    * ```database: str``` - the new default database/search path
* Example
    ```python
    v.use('mydatabase')
    ```
---

### *v.db()*

* Description: Returns a list of the databases available in the current instance
* Returns
    * ```vulkn.recordset.RecordSet```
* Example
    ```python
    >>> v.db().s

    row  name
    -----  -----------------
        1  billy
        2  cached
        3  database_for_dict
        4  default
        5  dicts
        6  system
        7  tmp
        8  vulkn

    (8 rows)
    ```
---

### v.tables(database: str), v.t(database: str)*

* Description: Returns a list of the tables available in the specified or current database (default)
* Parameters
    * ```database``` - the database to inspect
* Returns
    * ```vulkn.recordset.RecordSet```
* Example
    ```python
    >>> v.t('cached').s

    row  database    name    engine       partition_key  sorting_key
    -----  ----------  ------  ---------  ---------------  -------------
        1  cached      test    Log                    nan  nan
        2  cached      test1   MergeTree              nan  number

    (2 rows)
    ```
---

### *v.table_exists(database, table)*

* Description: Tests if the specified table exists
* Parameters
    * ```database``` - the database containing the object to test
    * ```table``` - the table/object to test
* Returns
    * ```bool```
* Example
    ```python
    v.table_exists('default', 'test')
    False
    ```
---

### *v.desc(table: str)*, *v.d(table: str)*

* Description: Describe the schema/configuration of the specified table.
* Aliases: ```v.d(table: str)```
* Parameters
    * ```table: str``` - the new default database/search path
* Returns
    * ```vulkn.recordset.RecordSet```
* Example
    ```python
    >>> v.desc('system.databases').s

    row  name           type      default_type    default_expression    comment    codec_expression    ttl_expression
    -----  -------------  ------  --------------  --------------------  ---------  ------------------  ----------------
        1  name           String             nan                   nan        nan                 nan               nan
        2  engine         String             nan                   nan        nan                 nan               nan
        3  data_path      String             nan                   nan        nan                 nan               nan
        4  metadata_path  String             nan                   nan        nan                 nan               nan

    (4 rows)
    ```
---

### *v.get_create(table: str)*

* Description: Get the CREATE statement for the table or object
* Parameters
    * ```table: str``` - the new default database/search path
* Returns
    * ```str```
* Example
    ```python
    >>> v.get_create('default.timeseries')
    "CREATE TABLE default.timeseries\n(\n    `key` String, \n    `ts` DateTime('Australia/Melbourne'), \n    `value` UInt32\n)\nENGINE = MergeTree\nPARTITION BY toStartOfDay(ts)\nORDER BY (key, ts)\nSETTINGS index_granularity = 8192;
    ```
---

### *v.show_create(table: str)*, *v.c(table: str)*

* Description: Show/pretty print the CREATE statement for the table or object
* Aliases: ```v.c(table: str)```
* Parameters
    * ```table: str``` - the new default database/search path
* Returns
    * ```str```
* Example
    ```python
    >>> v.show_create('default.timeseries')
    CREATE TABLE default.timeseries
    (
        `key` String, 
        `ts` DateTime('Australia/Melbourne'), 
        `value` UInt32
    )
    ENGINE = MergeTree
    PARTITION BY toStartOfDay(ts)
    ORDER BY (key, ts)
    SETTINGS index_granularity = 8192;
    ```
---

### *v.get_schema(database: str=None, table: str=None)*

* Description: Returns a list of the table schema suitable for the reader interface.
* Parameters
    * ```database: str``` - the database where the table can be found
    * ```table: str``` - the table to inspect
* Returns
    * ```list[ColumnType]```
* Example
    ```python
    >>> pprint.pprint(v.get_schema('default', 'timeseries'))
    [ColumnType('key', 'String', default_kind='nan', default_expression='nan' compression_codec='nan'),
     ColumnType('ts', 'DateTime(\'Australia/Melbourne\')', default_kind='nan', default_expression='nan' compression_codec='nan'),
     ColumnType('value', 'UInt32', default_kind='nan', default_expression='nan' compression_codec='nan')]
    ```
---

### *v.optimize(database: str, table: str, partition=None, final=False, deduplicate=False)*

* Description: Executes the OPTIMIZE operation on the specified database.table [optional partition]
* Parameters
    * ```database``` - the database containing the table to inspect
    * ```table``` - the table to optimize
    * ```partition``` - the optional partition of the table to optimize
    * ```final``` - whether to execute in OPTIMIZE FINAL mode
    * ```deduplicate``` - whether to execute in OPTIMIZE DEDUPLICATE mode
* Returns
    * ```bool```
* Example
    ```python
    >>> v.optimize('default', 'timeseries')
    True
    ```
---

### *v.parts(database=None, table=None)*

* Description: Returns a list of the parts for the specified database.table. 
* Parameters
    * ```database``` - the database containing the table
    * ```table``` - the table to inspect
* Returns
    * ```vulkn.recordset.RecordSet```
* Example
    ```python
    >>> v.parts('default', 'iot_nw_netflow').s
      row  partition         rows  path
    -----  -----------  ---------  -----------------------------------------------------------------------------
        1  2019-10-01   354001673  /var/lib/clickhouse/data/default/iot_nw_netflow/20191001_1809_2141_5_12328/
        2  2019-10-02   344417952  /var/lib/clickhouse/data/default/iot_nw_netflow/20191002_2142_3127_5_12328/
        3  2019-10-03   349287299  /var/lib/clickhouse/data/default/iot_nw_netflow/20191003_2151_3095_5_12328/
        4  2019-10-04   353890586  /var/lib/clickhouse/data/default/iot_nw_netflow/20191004_2170_3121_5_12328/
        5  2019-10-05   351980346  /var/lib/clickhouse/data/default/iot_nw_netflow/20191005_3128_4419_5_12328/
        6  2019-10-06   337347169  /var/lib/clickhouse/data/default/iot_nw_netflow/20191006_3139_4444_5_12328/
        7  2019-10-07   360367914  /var/lib/clickhouse/data/default/iot_nw_netflow/20191007_3140_4445_6_12328/
        8  2019-10-08   350891850  /var/lib/clickhouse/data/default/iot_nw_netflow/20191008_4446_5097_5_12328/
        9  2019-10-09   353855520  /var/lib/clickhouse/data/default/iot_nw_netflow/20191009_4456_5108_5_12328/
       10  2019-10-10   349907606  /var/lib/clickhouse/data/default/iot_nw_netflow/20191010_5109_5765_5_12328/

    (10 rows)
    ```
---

### *v.clone_table(from_database, from_table, database, table)*

* Description: Copies a table definition only from database.table to another.
* Parameters
    * ```from_database``` - the source database to clone from
    * ```from_table``` - the source table to clone from
    * ```database``` - the target database to clone to
    * ```table``` - the target table to clone to
* Returns
    * ```bool```
* Example
    ```python
    >>> v.clone_table('default', 'iot_nw_netflow', 'other', 'iot_nw_netflow2')
    True
    ```
---

### *v.copy_table(from_database, from_table, database, table)*

* Description: Copies a table, including it's data, from the source table to the targe table
* Parameters
    * ```from_database``` - the source database to copy from
    * ```from_table``` - the source table to copy from
    * ```database``` - the target database to copy to
    * ```table``` - the target table to copy to
* Returns
    * ```bool```
* Example
    ```python
    >>> v.copy_table('default', 'iot_nw_netflow', 'other', 'iot_nw_netflow2')
    True
    ```
---

### *v.create_table(database=None, table=None, schema=None, engine=None, exists_ok=False)*

* Description: Creates a new table
* Parameters
    * ```database``` - the database to create the table in
    * ```table``` - the table name
    * ```schema``` - the schema ColumnType definition
    * ```engine``` - the database engine definition
    * ```exists_ok``` - don't error if the table already exists
* Returns
    * ```bool```
* Example
    ```python
    >>> v.create_table('default', 'iot_nw_netflow3', v.getSchema('default', 'iot_nw_netflow'), engines.Memory())
    True
    ```
---

### *v.create_view(database, view, query, exists_ok=False)*

* Description: Creates a new view based on the specified query
* Parameters
    * ```database``` - the database to create the table in
    * ```view``` - the view name
    * ```query``` - the source query for the view - can be a DataTable
    * ```exists_ok``` - don't error if the table already exists
* Returns
    * ```bool```
* Example
    ```python
    >>> vdef = 'SELECT count() FROM myrecords'
    >>> v.create_view('default', 'myview', vdef)
    True
    ```
---

### *v.create_mat_view(database, view, query, to_database, to_table, engine, exists_ok)*

* Description: Creates a new materialized view in the target database with name view using the specified query
* Parameters
    * ```database``` - the database to create the table in
    * ```view``` - the materialized view name
    * ```query``` - the source query for the MatView
    * ```to_database``` - the database to write the result table in
    * ```to_table``` - the table to write the result table to
    * ```engine``` - the database engine definition
    * ```exists_ok``` - don't error if the table already exists
* Returns
    * ```bool```
* Example
    ```python
    >>> mv_def = 'SELECT device_id, substring(def_col), count() FROM myrecords'
    >>> v.create_mat_view('default', 'mymatview', mv_def, 'default', 'targettable', engines.MergeTree())
    True
    ```
---

### *v.create_sink(database, sink, schema, exists_ok=False)*

* Description: Creates a new input sink (table with the Null engine) suitable for streaming input with transformations.
* Parameters
    * ```database``` - the database to create the table in
    * ```table``` - the table name
    * ```schema``` - the schema ColumnType definition
    * ```exists_ok``` - don't error if the table already exists
* Returns
    * ```bool```
* Example
    ```python
    >>> v.create_sink('default', 'netflow_sink', v.getSchema('default', 'iot_nw_netflow'))
    True
    ```
---

### *v.drop_table(database, table)*, *drop_sink*, *drop_view*, *drop_mat_view*

* Description: Drops the specified table/object.
* Parameters
    * ```database``` - the database containing the object to drop
    * ```table``` - the table/object to remove
* Returns
    * ```bool```
* Example
    ```python
    v.drop_table('default','old_table')
    True
    ```
---

### *v.drop_part(database=None, table=None, partitions=None)*

* Description: Drops the specified partitions from the table
* Parameters
    * ```database``` - the database containing the required table
    * ```table``` - the table to call the drop operation on
    * ```partitions: list``` - a list of partitions to drop
* Returns
    * ```bool```
* Example
    ```python
    v.drop_part('default','trades_2015',partitions=['2015-02-01','2015-03-01'])
    True
    ```
---

### *v.drop_columns(database, table, \*columns)*

* Description: Drops the specified columns from the table
* Parameters
    * ```database``` - the database containing the required table
    * ```table``` - the table to call the drop operation on
    * ```columns: list``` - a list of columns to drop
* Returns
    * ```bool```
* Example
    ```python
    v.drop_columns('default','trades_2015',['city','state'])
    True
    ```
---

### *v.truncate_table(database, table)*

* Description: Truncates the specified table.
* Parameters
    * ```database``` - the database containing the object to truncate
    * ```table``` - the table/object to truncate
* Returns
    * ```bool```
* Example
    ```python
    v.truncate_table('default', 'truncateme')
    True
    ```
---
