# DataTable Reference

## *q(query: str)*

* Parameters:
    * ```query: str``` - a valid ClickHouse or Vulkn SQL string.
* Returns: ```vulkn.datatable.QueryStringDataTable```
* Examples
    ```python
    v.q('SELECT * FROM system.tables LIMIT 1').show()
    ```
---

The ```q``` method accepts an SQL query string and can be used to execute standard SQL queries against a ClickHouse or Workspace.

See ClickHouse reference - [SELECT Clause](https://clickhouse.yandex/docs/en/query_language/select/)

### SelectQueryDataTable Methods

The q DataTable also supports the following SelectQueryDataTable methods returning a new SelectQueryDataTable
object. See the SelectQueryDataTable methods in the select DataTable section for further detail on
parameters and usage.

SelectQueryDataTable clause | Description | Example
-- | -- | --
limit | Limits the number of results by the specified number | ```v.q('SELECT * FROM system.tables').limit(1).s``` |
where, filter | Applies the specified filter to the DataTable | ```v.q('SELECT * FROM system.tables').where("database = 'default'").s``` |
limit_by | Limits the results by the specified number by the specified key | ```v.q('SELECT * FROM system.tables').limit_by(1, ('database',)).s``` |
first | Returns the first value found within the DataTable | ```v.q('SELECT * FROM system.tables').first().s``` |
head | Returns the Nth first values within the DataTable | ```v.q('SELECT * FROM system.tables').head(2).s``` |
distinct | Returns only the unique values/rows | ```v.q('SELECT database FROM system.tables').distinct().s``` |
order_by, sort | Sorts the specified DataTable by the specified key(s) | ```v.q('SELECT database FROM system.tables').distinct().order_by('database').s``` |
prewhere | Applies column filtering prior to the where clause | ```v.q('SELECT * FROM default.mergetree').prewhere('is_valid = 1').s``` |

---

## *BaseTableDataFrame*

BaseTableDataFrames are entry points for the SelectQueryDataTable type that is detailed later in this
section.

BaseTableDataFrames are created using either the v.table() method or the v.data dunder dictionary.

These support two additional methods.

### *desc()*

* Description: Provides a description of the data definition for the table.
* Returns: ```vulkn.recordset.RecordSet```
* Example:
    ```python
    v.table('default.baz').desc().s

      row  name    type      default_type    default_expression    comment    codec_expression    ttl_expression
    -----  ------  ------  --------------  --------------------  ---------  ------------------  ----------------
        1  id      String             nan                   nan        nan                 nan               nan
        2  a       String             nan                   nan        nan                 nan               nan
        3  b       String             nan                   nan        nan                 nan               nan

    (3 rows)
    ```
---

### *drop_columns(\*columns)*

* Description: Drops the specified columns from the table.
* Returns: ```bool```
* Example:
    ```python
    >>> v.table('default.baz').drop_columns('a','b')
    True
    >>> v.table('default.baz').desc().s

      row  name    type      default_type    default_expression    comment    codec_expression    ttl_expression
    -----  ------  ------  --------------  --------------------  ---------  ------------------  ----------------
        1  id      String             nan                   nan        nan                 nan               nan

    (1 row)
    ```
---

### *load(parts=[])*

* Description: Loads a whole table or part of a table into memory.
* Parameters: ```parts``` - optional - a list of parts to load from the table.
* Returns: ```BaseTableDataFrame```
* Example:
    ```python
    >>> t = v.table('default.baz').load(parts=['20190101','20190102'])
    ```
---

## *one*

* Returns: ```vulkn.datatable.SelectQueryDataTable```
* Example:
    ```python
    v.one().s
    ```
---

Returns a single row/column 'dummy'. Equivalent to the SQL ```SELECT * FROM system.one```.

## *numbers(count: int, system: bool=False, mt: bool=False)*

* Parameters:
    * ```count: int``` - the number of numbers starting from 0 to return
    * ```system: bool=False``` - use the system.numbers variant as opposed to the numbers() table function
    * ```mt: bool=False``` - use the multi-threaded versions of the system and numbers() calls
* Returns: ```vulkn.datatable.SelectQueryDataTable```
---

## *range(start: int, end: int, system: bool=False, mt: bool=False)*

* Parameters:
    * ```start: int``` - the first number in the range to return. May be negative.
    * ```end: int``` - the last number in the range to return. May be negative.
    * ```system: bool=False``` - use the system.numbers variant as opposed to the numbers() table function
    * ```mt: bool=False``` - use the multi-threaded versions of the system and numbers() calls
* Returns: ```vulkn.datatable.SelectQueryDataTable```
---

## *random(count: int, start=0, end=18446744073709551615, system=False, mt=False)*

* Parameters:
    * ```count: int``` - the number of random numbers to generate
    * ```start: int=0``` - the lower bound for the random numbers (default = 0)
    * ```end: int=0``` - the upper bound for the random numbers (default = UInt64.max)
    * ```system: bool=False``` - use the system.numbers variant as opposed to the numbers() table function
    * ```mt: bool=False``` - use the multi-threaded versions of the system and numbers() calls
* Returns: ```vulkn.datatable.SelectQueryDataTable```
---

## *randfloat(count: int, start=0, end=18446744073709551615, system=False, mt=False)*

* Parameters:
    * ```count: int``` - the number of random numbers to generate
    * ```start: int=0``` - the lower bound for the random numbers (default = 0)
    * ```end: int=0``` - the upper bound for the random numbers (default = UInt64.max)
    * ```system: bool=False``` - use the system.numbers variant as opposed to the numbers() table function
    * ```mt: bool=False``` - use the multi-threaded versions of the system and numbers() call
* Returns: ```vulkn.datatable.SelectQueryDataTable```
---

## *select(\*cols)*, *table('database.table')*, *data.database.table*, *data['database.table']*

* Parameters:
    * ```cols: str, column literal, column expression or datatype/variable``` - a column list
    * ```tablename: str``` - the table to query from
* Returns: ```vulkn.datatable.SelectQueryDataTable```
* Examples
    ```python
    v.select('*').from_('system.tables').limit(1).s

    v.table('system.tables').select('*').limit(1).s

    v.data.system.tables.select('*').limit(1).s

    v.data['system.tables'].select('*').limit(1).s
    ```
---

These ```select``` entrypoint accepts a list of column variables as normally found within the SELECT SQL 
projection clause. The column variables can be anything from Python types (excluding dictionaries), 
string column names, string column expressions, column literals or column expressions (using the types.col 
object) or any valid Vulkn datatype (String, UInt8 etc..).

The ```table``` and ```data``` entrypoints accept a schema qualified tablename. These return a BaseTableDataTable.

These entrypoints provide an Object Relational Mapper (ORM) style interface for executing queries.

See ClickHouse reference - [SELECT Clause](https://clickhouse.yandex/docs/en/query_language/select/)

### *with_(\*cols)*

* Parameters:
    * ```cols: list``` - list of str, column literal, column expression or datatype/variables
* Returns: ```vulkn.datatable.SelectQueryDataTable```
---

See ClickHouse reference - [WITH Clause](https://clickhouse.yandex/docs/en/query_language/select/#with-clause)

!!! note "Examples"
    **SQL**
    ```sql
    WITH
        sum(data_compressed_bytes) AS sum_bytes
    SELECT
        formatReadableSize(sum_bytes) AS total_size
    FROM system.parts
    ```
    **Raw Query**
    ```python
    v.q('with sum(data_compressed_bytes) as sum_bytes select formatReadableSize(sum_bytes) as total_size from system.parts').s
    ```
    **DataTable**
    ```python
    (v.table('system.parts')
        .with_(funcs.agg.sum(c('data_compressed_bytes')).alias('sum_bytes'))
        .select(funcs.formatReadableSize(c('sum_bytes')).alias('total_size')).s)
    ```

### *distinct()*

* Returns: ```vulkn.datatable.SelectQueryDataTable```

---

See ClickHouse reference - [DISTINCT Clause](https://clickhouse.yandex/docs/en/query_language/select/#distinct-clause)

!!! note "Examples"
    **SQL**
    ```sql
    SELECT DISTINCT database FROM system.tables
    ```
    **Raw Query**
    ```python
    v.q("select distinct database from system.tables").s
    ```
    **DataTable**
    ```python
    v.table('system.tables').select('database').distinct().s

    row  name
    -----  --------
        1  clusters

    (1 row)
    ```

### *array_join(\*array_expressions)*

* Returns: ```vulkn.datatable.SelectQueryDataTable```

---

See ClickHouse reference - [ARRAY JOIN Clause](https://clickhouse.yandex/docs/en/query_language/select/#select-array-join-clause)

!!! note "Examples"
    **SQL**
    ```sql
    SELECT k, n
    FROM (SELECT groupArray(number) AS n FROM numbers(10))
    ARRAY JOIN n AS k
    ```
    **Raw Query**
    ```python
    v.q("""
        SELECT k, n
        FROM (SELECT groupArray(number) AS n FROM numbers(10))
        ARRAY JOIN n AS k
    """).s
    ```
    **DataTable**
    ```python
    (v.numbers(10)
        .select(funcs.agg.groupArray(c('number')).alias('n'))
        .select('k', 'n')
        .array_join(c('n').alias('k')).s)

      row    k  n
    -----  ---  ---------------------
        1    0  [0,1,2,3,4,5,6,7,8,9]
        2    1  [0,1,2,3,4,5,6,7,8,9]
        3    2  [0,1,2,3,4,5,6,7,8,9]
        4    3  [0,1,2,3,4,5,6,7,8,9]
        5    4  [0,1,2,3,4,5,6,7,8,9]
        6    5  [0,1,2,3,4,5,6,7,8,9]
        7    6  [0,1,2,3,4,5,6,7,8,9]
        8    7  [0,1,2,3,4,5,6,7,8,9]
        9    8  [0,1,2,3,4,5,6,7,8,9]
       10    9  [0,1,2,3,4,5,6,7,8,9]

    (10 rows)
    ```

### *left_array_join(\*array_expressions)*

* Returns: ```vulkn.datatable.SelectQueryDataTable```

---

See ClickHouse reference - [ARRAY JOIN Clause](https://clickhouse.yandex/docs/en/query_language/select/#select-array-join-clause)

!!! note "Examples"
    **SQL**
    ```sql
    SELECT k, n
    FROM (SELECT groupArray(number) AS n FROM numbers(10))
    ARRAY JOIN n AS k
    ```
    **Raw Query**
    ```python
    v.q("""
        SELECT k, n
        FROM (SELECT groupArray(number) AS n FROM numbers(10))
        ARRAY JOIN n AS k
    """).s
    ```
    **DataTable**
    ```python
    # array_join returns only those rows where their array lengths are > 0 (as per an INNER JOIN)
    (v.q("""
        SELECT 'Hello' AS s, [1,2] AS arr UNION ALL
        SELECT 'World', [3,4,5] UNION ALL
        SELECT 'Goodbye', []""")
    .select('s', 'arr')
    .array_join('arr').s)

      row  s        arr
    -----  -----  -----
        1  Hello      1
        2  Hello      2
        3  World      3
        4  World      4
        5  World      5  

    (5 rows)

    # left_array_join returns all rows, including those with zero length arrays (as per LEFT JOIN)
    (v.q("""
        SELECT 'Hello' AS s, [1,2] AS arr UNION ALL
        SELECT 'World', [3,4,5] UNION ALL
        SELECT 'Goodbye', []""")
    .select('s', 'arr')
    .left_array_join('arr').s)

      row  s        arr
    -----  -----  -----
        1  Hello      1
        2  Hello      2
        3  World      3
        4  World      4
        5  World      5  
        6  Goodbye    0

    (6 rows)
    ```

### *where(\*col_filters)*, *filter(\*col_filters)*

* Parameters:
    * ```col_filters: list```- List of column filters as str, column literal, column expression or datatype/variable or function
* Returns: ```vulkn.datatable.SelectQueryDataTable```
---

See ClickHouse reference - [WHERE Clause](https://clickhouse.yandex/docs/en/query_language/select/#where-clause)

!!! note "Examples"
    **SQL**
    ```sql
    SELECT
        name
    FROM system.tables
    WHERE name = 'clusters'
    ```
    **Raw Query**
    ```python
    v.q("select name from system.tables where name = 'clusters'").s
    ```
    **DataTable**
    ```python
    v.table('system.tables').select('name').where(c('name') == 'clusters').s

    row  name
    -----  --------
        1  clusters

    (1 row)
    ```
    ```python
    v.table('system.tables').select('name').filter(c('name') == 'clusters', c('database') == 'system').s

    row  name
    -----  --------
        1  clusters

    (1 row)
    ```

### *prewhere(\*col_filters)*

* Parameters:
    * ```col_filters: list```- List of column filters as str, column literal, column expression or datatype/variable or function
* Returns: ```vulkn.datatable.SelectQueryDataTable```
---

See ClickHouse reference - [PREWHERE Clause](https://clickhouse.yandex/docs/en/query_language/select/#prewhere-clause)

!!! note "Example"
    **DataTable**
    ```python
    df = v.table('example').select('*').prewhere().s
    ```

### *group_by(\*cols [, with_totals=False])*

* Parameters:
    * ```cols: list``` - List of columns as str, column literal, column expression or datatype/variable or function
    * ```with_totals: bool``` - Include additional whole of group aggregate row (default False)
* Returns: ```vulkn.datatable.SelectQueryDataTable```
---

group_by operates exactly as per the SQL ```GROUP BY``` statement. The keys defined in the group_by
clause specify a distinct tuple arrangement whilst other columns must be aggregated by some function.

See ClickHouse reference - [GROUP BY Clause](https://clickhouse.yandex/docs/en/query_language/select/#select-group-by-clause)

The following are equivalent:

!!! note "Examples"
    **SQL**
    ```sql
    SELECT
        database,
        count()
    FROM system.tables
    GROUP BY database
    ```
    **Raw Query**
    ```python
    v.q('select database, count() from system.tables group by database').s
    ```
    **DataTable**
    ```python
    v.table('system.tables').select('database',funcs.agg.count()).group_by('database').s

      row    database    count()
    -----  ----------  ---------
        1  system             35
        2  vulkn               1

    (2 rows)

    (v.table('system.tables')
        .select('database',funcs.agg.count())
        .group_by('database', with_totals=True).s)

      row    database    count()
    -----  ----------  ---------
        1  system             35
        2  vulkn               1
        3  nan                36

    (3 rows)
    ```

### *having(\*col_filters)*

* Parameters:
    * ```col_filters: list```- List of column filters as str, column literal, column expression or datatype/variable or function
* Returns: ```vulkn.datatable.SelectQueryDataTable```
---

See ClickHouse reference - [HAVING Clause](https://clickhouse.yandex/docs/en/query_language/select/#having-clause)

The ```HAVING``` function/statement is an optional filter that can be applied to the results of a 
```GROUP BY``` aggregation.

The following are equivalent:

!!! note "Examples"
    **SQL**
    ```sql
    SELECT
        database,
        count() AS count
    FROM system.tables
    GROUP BY database
    HAVING count > 20
    ```
    **SQL**
    ```python
    v.q('select database, count() as count from system.tables group by database having count > 20').s
    ```
    **DataTable**
    ```python
    df = (v.table('system.tables')
        .select('database', funcs.agg.count().alias('count'))
        .group_by('database')
        .having('count > 20'))
    df.show()

    row  database      count
    -----  ----------  -------
        1  default          83
        2  system           39

    (2 rows)
    ```

### *order_by(\*cols)*, *sort(\*cols)*

* Parameters:
    * ```cols: list```- List of column filters as str, column literal, column expression or datatype/variable or function
* Returns: ```vulkn.datatable.SelectQueryDataTable```
---

See ClickHouse reference - [ORDER BY Clause](https://clickhouse.yandex/docs/en/query_language/select/#select-order-by)

The following are equivalent:

!!! note "Examples"
    **SQL**
    ```sql
    SELECT
        name,
        engine,
        data_path 
    FROM system.databases 
    ORDER BY name
    LIMIT 2
    ```
    **Raw Query**
    ```python
    # Vulkn q DataTable
    v.q('select name, engine, data_path from system.databases order by name limit 2').s
    ```
    **DataTable**
    ```python
    # Vulkn select DataTable
    v.table('system.databases').select('name','engine','data_path').order_by('name').limit(2).s

    row  name     engine    data_path
    -----  -------  --------  ------------------------------------------------------------------------
        1  default  Ordinary  /tmp/ironman-f01d531f-1189-4db4-8bf9-04ccc85f7e10/clickhouse/data/default/
        2  system   Ordinary  /tmp/ironman-f01d531f-1189-4db4-8bf9-04ccc85f7e10/clickhouse/data/system/

    (2 rows)
    ```

### *limit(rows: int (, offset: int))*

* Parameters:<br/>
    * ```rows: int``` - number of rows to return
    * (optional) ```offset: int``` - allows skipping the first offset rows
* Returns: ```vulkn.datatable.SelectQueryDataTable```
---

See ClickHouse reference - [LIMIT Clause](https://clickhouse.yandex/docs/en/query_language/select/#limit-clause)

The following are equivalent:

!!! note "Examples"
    **SQL**
    ```sql
    SELECT
        name
    FROM system.tables
    LIMIT 3
    ```
    **Raw Query**
    ```python
    v.q('select name from system.tables limit 3').s
    ```
    **DataTable**
    ```python
    v.table('system.tables').select('name').limit(3).s

    row  name
    -----  ------------------------------
        1  aggregate_function_combinators
        2  asynchronous_metrics
        3  build_options

    (3 rows)
    ```

### *limit_by(rows: int, cols: tuple)*

* Parameters:<br/>
    * ```rows: int``` - number of rows to return for each key specified by ```cols```
    * ```cols: tuple``` - the grouping key to apply the sub-limit ```rows```
* Returns: ```vulkn.datatable.SelectQueryDataTable```
---

See ClickHouse reference - [LIMIT BY Clause](https://clickhouse.yandex/docs/en/query_language/select/#limit-by-clause)

The following are equivalent:


!!! note "Examples"
    **SQL**
    ```sql
    SELECT
        name
    FROM system.tables 
    LIMIT 3 BY database
    ```
    **Raw Query**
    ```python
    v.q('select name from system.tables limit 3 by database').s
    ```
    **DataTable**
    ```python
    df = v.table('system.tables').select('database','name').limit_by(3, ('database',)).s
    ```

### Special methods

#### *all()*

* Returns: ```vulkn.datatable.SelectQueryDataTable```
* Description: Valid only for base tables. Inspects the base table and determines returns all columns irrespective of column type (materialized, alias)
* Example:
    ```python
    v.table('default.table_with_aliases').all().limit(3).s
    ```

#### *count()*

* Returns: ```vulkn.datatable.SelectQueryDataTable```
* Description: Short-hand command for the total number of records in the datatable. It is equvalent to the SQL ```SELECT count() FROM table```.
* Example:
    ```python
    v.table('system.tables').count().s
    ```

#### *first()*

* Returns: ```vulkn.datatable.SelectQueryDataTable```
* Description: Short-hand command for returning the first record in the datatable. Note that a column specification list is required.
* Example:
    ```python
    v.table('system.tables').all().first().s
    ```

#### *head(rows: int=1)*

* Parameters:
    * ```rows: int=1``` - the number of rows to return from the DataTable. Default 1.
* Returns: ```vulkn.datatable.SelectQueryDataTable```
* Description: Identical to limit(). Note that a column specification list is required.
* Example:
    ```python
    v.table('system.tables').all().head(3).s
    ```

## Vulkn Extensions

The following are Vulkn core extensions not found within the ClickHouse SQL dialect.

### *vectorize_by(key, [non-key-columns, ..,] sort)*

* Parameters
    - ```key``` - key to group vector columns by.
    - ```non-key-columns``` - Optional. A list of additional columns that are neither key, sort or vector columns.
    - ```sort``` - column to sort on within each key group.
* Returns: ```vulkn.datatable.SelectQueryDataTable```
---

```VECTORIZE BY``` is a Vulkn extension to ClickHouse SQL. It operates in a manner similar to a 
```GROUP BY``` operation however it returns every row in the set (without aggregates). Specialised vector
functions are used in place of aggregates and enable each row to have visibility with respect
to all rows for the current key. This enables rudimentary SQL:2003 Window Functions and other 
specialized time-series operations across arrays.

**Example**

Given the following dataset:

```python
key = ArrayVector.range(1,3).take(15).sort().cache().alias('key')
timestamp = ArrayVector.rand(DateTime('2019-01-01 00:00:00'),DateTime('2019-01-01 23:59:59'),15).cast(DateTime).cache().alias('timestamp')
metric = ArrayVector.rand(1,8192,15).cache().alias('metric')

df = v.table.fromVector('default.vector_example', (key, timestamp, metric))
df.select('*').order_by('key','timestamp').show()

  row    key  timestamp              metric
-----  -----  -------------------  --------
    1      1  2019-01-01 00:50:58      1991
    2      1  2019-01-01 02:56:46      4679
    3      1  2019-01-01 03:01:30      2722
    4      1  2019-01-01 12:19:14      8136
    5      1  2019-01-01 22:18:44       164
    6      2  2019-01-01 03:34:21      2980
    7      2  2019-01-01 17:12:50      4646
    8      2  2019-01-01 18:13:29      7144
    9      2  2019-01-01 18:39:45      4208
   10      2  2019-01-01 23:47:01       498
   11      3  2019-01-01 09:46:18      1444
   12      3  2019-01-01 10:42:01      2709
   13      3  2019-01-01 21:18:15      2498
   14      3  2019-01-01 21:31:15      5133
   15      3  2019-01-01 22:41:53      5042

(15 rows)
```

If we wish to calculate the delta between successive items within the same key ```VECTORIZE BY```
can be used to create sub-vectors of the timestamp and metric columns upon which we can apply a 
```vectorDelta``` operation.

```python
(df.select('key', 'timestamp', 'metric',
           funcs.vector.vectorDelta(c('metric')).alias('metric_delta'))
.vectorize_by('key','timestamp')).s

  row    key  timestamp              metric    metric_delta
-----  -----  -------------------  --------  --------------
    1      3  2019-01-01 09:46:18      1444             nan
    2      3  2019-01-01 10:42:01      2709            1265
    3      3  2019-01-01 21:18:15      2498            -211
    4      3  2019-01-01 21:31:15      5133            2635
    5      3  2019-01-01 22:41:53      5042             -91
    6      2  2019-01-01 03:34:21      2980             nan
    7      2  2019-01-01 17:12:50      4646            1666
    8      2  2019-01-01 18:13:29      7144            2498
    9      2  2019-01-01 18:39:45      4208           -2936
   10      2  2019-01-01 23:47:01       498           -3710
   11      1  2019-01-01 00:50:58      1991             nan
   12      1  2019-01-01 02:56:46      4679            2688
   13      1  2019-01-01 03:01:30      2722           -1957
   14      1  2019-01-01 12:19:14      8136            5414
   15      1  2019-01-01 22:18:44       164           -7972

(15 rows)
```

The above is equivalent to:

```python
v.q("""
    select
        key,
        timestamp,
        metric,
        vectorDelta(metric) as metric_delta
    from default.vector_example
    vectorize by (key, timestamp)""")
```

Note that there are no guarantees that the result will be ordered by key, only the values within 
each key vector will be ordered (by timestamp). To return values ordered by key you can wrap the 
call in an additional DataTable operation:

```python
((df.select('key', 'timestamp', 'metric',
            funcs.vector.vectorDelta(c('metric')).alias('metric_delta'))
    .vectorize_by('key','timestamp'))
.select('*').order_by('key','timestamp').s)

  row    key  timestamp              metric    metric_delta
-----  -----  -------------------  --------  --------------
    1      1  2019-01-01 00:50:58      1991             nan
    2      1  2019-01-01 02:56:46      4679            2688
    3      1  2019-01-01 03:01:30      2722           -1957
    4      1  2019-01-01 12:19:14      8136            5414
    5      1  2019-01-01 22:18:44       164           -7972
    6      2  2019-01-01 03:34:21      2980             nan
    7      2  2019-01-01 17:12:50      4646            1666
    8      2  2019-01-01 18:13:29      7144            2498
    9      2  2019-01-01 18:39:45      4208           -2936
   10      2  2019-01-01 23:47:01       498           -3710
   11      3  2019-01-01 09:46:18      1444             nan
   12      3  2019-01-01 10:42:01      2709            1265
   13      3  2019-01-01 21:18:15      2498            -211
   14      3  2019-01-01 21:31:15      5133            2635
   15      3  2019-01-01 22:41:53      5042             -91

(15 rows)

```

### *chunk_by(chunkkey: tuple, chunksize: int)*

* Parameters
    * ```chunkkey: tuple``` - the key or composite key to chunk on (using cityHash64)
    * ```chunksize: int``` - size of processing splits, generally no more than the number of CPU cores.
* Returns: ```vulkn.datatable.SelectQueryDataTable```
---

```CHUNK BY``` is a Vulkn extension that addresses some performance bottlenecks in ClickHouse in
cases where finalizing a function, generally an aggregation, results in utilization of only a 
single thread. This is only of use when a result or aggregation can be multiplexed by a key.

**Example**

When using histogram function across unique keys we can accelerate the execution by telling 
ClickHouse to split the query into multiple chunks/keys and process these independently.

Either of the following queries:

```python
v.table('timeseries_devices').select('key',funcs.agg.histogram(10, bytes)).group_by('key').chunk_by('key',2).s
v.q('select key, histogram(10)(bytes) from timeseries_devices group by key chunk by (key, 2)').s
```

Will be converted to the following valid ClickHouse SQL:

```sql
SELECT key, histogram(10)(bytes) FROM timeseries_devices WHERE cityHash64(key)%2 = 0 GROUP BY key
UNION ALL
SELECT key, histogram(10)(bytes) FROM timeseries_devices WHERE cityHash64(key)%2 = 1 GROUP BY key
```

Note that ```CHUNK BY``` will only work in specific cases and will be deprecated once the ClickHouse
core team address any lagging performance issues in this area.
