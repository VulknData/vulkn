# select

See ClickHouse reference - [SELECT Clause](https://clickhouse.yandex/docs/en/query_language/select/)

The ```select``` method provides an Object Relational Mapper (ORM) style interface for executing queries.

### Example

```python
df = v.table('example').select('*').show()
```

## Methods

### with_

See ClickHouse reference - [WITH Clause](https://clickhouse.yandex/docs/en/query_language/select/#with-clause)

```sql
-- SQL
WITH
    sum(data_compressed_bytes) AS sum_bytes
SELECT
    formatReadableSize(sum_bytes) AS total_size
FROM system.parts
```

```python
# Vulkn q DataFrame
v.q('with sum(data_compressed_bytes) as sum_bytes select formatReadableSize(sum_bytes) as total_size from system.parts').s
```

```python
(v.table('system.parts')
    .with_(funcs.agg.sum(c('data_compressed_bytes')).alias('sum_bytes'))
    .select(funcs.formatReadableSize(c('sum_bytes')).alias('total_size')).s)
```

### where, filter

See ClickHouse reference - [WHERE Clause](https://clickhouse.yandex/docs/en/query_language/select/#where-clause)

```sql
-- SQL
SELECT
    name
FROM system.tables
WHERE name = 'clusters'
```

```python
# Vulkn q DataFrame
v.q("select name from system.tables where name = 'clusters'").s
```

```python
# Vulkn select DataFrame
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

#### preWhere

See ClickHouse reference - [PREWHERE Clause](https://clickhouse.yandex/docs/en/query_language/select/#prewhere-clause)

```python
df = v.table('example').select('*').preWhere().s
```

### groupBy

See ClickHouse reference - [GROUP BY Clause](https://clickhouse.yandex/docs/en/query_language/select/#select-group-by-clause)

groupBy operates exactly as per the SQL ```GROUP BY``` statement. The keys defined in the groupBy
clause specify a distinct tuple arrangement whilst other columns must be aggregated by some function.

The following are equivalent:

```sql
-- SQL
SELECT
    database,
    count()
FROM system.tables
GROUP BY database
```

```python
# Vulkn q dataframe
v.q('select database, count() from system.tables group by database').s
```

```python
# Vulkn select dataframe
v.table('system.tables').select('database',funcs.agg.count()).groupBy('database').s

  row  database      count()
-----  ----------  ---------
    1  system             35
    2  vulkn               1

(2 rows)
```

#### having

See ClickHouse reference - [HAVING Clause](https://clickhouse.yandex/docs/en/query_language/select/#having-clause)

The ```HAVING``` function/statement is an optional filter that can be applied to the results of a 
```GROUP BY``` aggregation.

The following are equivalent:

```sql
-- SQL
SELECT
    database,
    count() AS count
FROM system.tables
GROUP BY database
HAVING count > 20
```

```python
# Vulkn q dataframe
v.q('select database, count() as count from system.tables group by database having count > 20').s
```

```python
df = (v.table('system.tables')
    .select('database', funcs.agg.count().alias('count'))
    .groupBy('database')
    .having('count > 20'))
df.show()

  row  database      count
-----  ----------  -------
    1  default          83
    2  system           39

(2 rows)
```

### vectorizeBy(key, [non-key-columns, ..,] sort)

- ```key``` - key to group vector columns by.
- ```non-key-columns``` - Optional. A list of additional columns that are neither key, sort or vector columns.
- ```sort``` - column to sort on within each key group.

```VECTORIZE BY``` is an Vulkn extension to ClickHouse SQL. It operates in a manner similar to a 
```GROUP BY``` operation however it returns every row in the set (without aggregates). Specialised vector
functions are used in place of aggregates and enable each row to have visibility with respect
to all rows for the current key. This enables rudimentary SQL:2003 Window Functions and other 
specialized time-series operations across arrays.

#### Example

Given the following dataset:

```python
key = ArrayVector.range(1,3).take(15).sort().cache().alias('key')
timestamp = ArrayVector.rand(DateTime('2019-01-01 00:00:00'),DateTime('2019-01-01 23:59:59'),15).cast(DateTime).cache().alias('timestamp')
metric = ArrayVector.rand(1,8192,15).cache().alias('metric')

df = v.table.fromVector('default.vector_example', (key, timestamp, metric))
df.select('*').orderBy('key','timestamp').show()

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
.vectorizeBy('key','timestamp')).s

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
call in an additional DataFrame operation:

```python
((df.select('key', 'timestamp', 'metric',
            funcs.vector.vectorDelta(c('metric')).alias('metric_delta'))
    .vectorizeBy('key','timestamp'))
.select('*').orderBy('key','timestamp').s)

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

### chunkBy

```CHUNK BY``` is a Vulkn extension that addresses some performance bottlenecks in ClickHouse in
cases where finalizing a function, generally an aggregation, results in utilization of only a 
single thread. This is only of use when a result or aggregation can be multiplexed by a key.

Example

Histograms are unable to.

```sql
SELECT key, histogram(10)(bytes) FROM timeseries_devices WHERE cityHash64(key)%2 = 0 GROUP BY key
UNION ALL
SELECT key, histogram(10)(bytes) FROM timeseries_devices WHERE cityHash64(key)%2 = 1 GROUP BY key
```

```python
v.q('select key, histogram(10)(bytes) from timeseries_devices group by key chunk by (key, 2)').s
```

```python
v.table('timeseries_devices').select('key',funcs.agg.histogram(10, bytes)).groupBy('key').chunkBy('key',2).s
```

### orderBy, sort

The following are equivalent:

```sql
-- SQL
SELECT
    name,
    engine,
    data_path 
FROM system.databases 
ORDER BY name
LIMIT 2
```

```python
# Vulkn q DataFrame
v.q('select name, engine, data_path from system.databases order by name limit 2').s
```

```python
# Vulkn select DataFrame
v.table('system.databases').select('name','engine','data_path').orderBy('name').limit(2).s

  row  name     engine    data_path
-----  -------  --------  ------------------------------------------------------------------------
    1  default  Ordinary  /tmp/ironman-f01d531f-1189-4db4-8bf9-04ccc85f7e10/clickhouse/data/default/
    2  system   Ordinary  /tmp/ironman-f01d531f-1189-4db4-8bf9-04ccc85f7e10/clickhouse/data/system/

(2 rows)
```

### limit

The following are equivalent:

```sql
-- SQL
SELECT
    name
FROM system.tables
LIMIT 3
```

```python
# Vulkn q DataFrame
v.q('select name from system.tables limit 3').s
```

```python
# Vulkn select DataFrame
v.table('system.tables').select('name').limit(3).s

  row  name
-----  ------------------------------
    1  aggregate_function_combinators
    2  asynchronous_metrics
    3  build_options

(3 rows)
```

### limitBy


```sql
-- SQL
SELECT
    name
FROM system.tables 
LIMIT 3 BY database
```

```python
# Vulkn q DataFrame
v.q('select name from system.tables limit 3 by database').s
```

```python
df = v.table('system.tables').select('database','name').limitBy(3, ('database',)).s
```

### params
### count

```count()``` is a short-hand command for returning the total number of records in a table.
It is equvalent to the SQL ```SELECT count() FROM table```.

### first
### head

## Joins
### join(jointype, right, keys, strictness=JoinStrictNess.All, global_mode=False)

- ```jointype``` - JoinType.(Left | Right | LeftInner | RightInner | Inner | Join | LeftOuter | RightOuter | Full | FullOuter | Cross).
- ```right``` - DataFrame - the right DataFrame to join on. 
- ```keys``` - tuple(keys, ...) - the keys to use in the join condition.
- ```strictness``` - JoinStrictNess.(Any | All | AsOf | Default). Default - JoinStrictNess.All
- ```global_mode``` - Boolean value indicating whether to use GLOBAL mode. Default - False.

```sql
-- SQL
SELECT 
    a.data_path, 
    b.database, 
    b.name AS table_name
FROM system.databases AS a
GLOBAL ANY LEFT JOIN system.tables AS b ON a.name = b.database
```

```python
# Vulkn q DataFrame
v.q("""
    select
        a.data_path,
        b.database,
        b.name as table_name
    from system.databases as a
    global any left join system.tables as b on a.name = b.database""").s
```

```python
d = v.table('system.databases').select('data_path',c('name').alias('database'))
t = v.table('system.tables').select('database',c('name').alias('table_name'))
d.join(JoinType.Left, t, ('database',), strictness=JoinStrictness.Any, global_mode=True).s
```

### ej (equi-join) (right, keys, strictness=JoinStrictNess.All, global_mode=False)

- ```right``` - DataFrame - the right DataFrame to join on.
- ```keys``` - tuple(keys, ...) - the keys to use in the join condition.
- ```strictness``` - JoinStrictNess.(Any | All | AsOf | Default). Default - JoinStrictNess.All
- ```global_mode``` - Boolean value indicating whether to use GLOBAL mode. Default - False.

```sql
-- SQL
SELECT 
    a.data_path, 
    b.database, 
    b.name AS table_name
FROM system.databases AS a
INNER JOIN system.tables AS b ON a.name = b.database
```

```python
# Vulkn q DataFrame
v.q("""
    select
        a.data_path,
        b.database,
        b.name as table_name
    from system.databases as a
    join system.tables as b on a.name = b.database""").s
```

```python
# Vulkn select DataFrame
d = v.table('system.databases').select('data_path',c('name').alias('database'))
t = v.table('system.tables').select('database',c('name').alias('table_name'))
d.ej(t, ('database',)).s
```

### rj (right-join) (left, keys, strictness=JoinStrictNess.All, global_mode=False)

- ```left``` - DataFrame - the left DataFrame to join on.
- ```keys``` - tuple(keys, ...) - the keys to use in the join condition.
- ```strictness``` - JoinStrictNess.(Any | All | AsOf | Default). Default - JoinStrictNess.All
- ```global_mode``` - Boolean value indicating whether to use GLOBAL mode. Default - False.

```sql
-- SQL
SELECT
    name
FROM system.tables
LIMIT 3 BY database
```

```python
# Vulkn q DataFrame
v.q('select name from system.tables limit 3 by database').s
```

```python
df = v.table('system.tables').select('database','name').limitBy(3, ('database',)).s
```

### lj (left-join) (right, keys, strictness=JoinStrictNess.All, global_mode=False)

- ```right``` - DataFrame - the right DataFrame to join on.
- ```keys``` - tuple(keys, ...) - the keys to use in the join condition.
- ```strictness``` - JoinStrictNess.(Any | All | AsOf | Default). Default - JoinStrictNess.All
- ```global_mode``` - Boolean value indicating whether to use GLOBAL mode. Default - False.

```sql
-- SQL
SELECT
    name
FROM system.tables
LIMIT 3 BY database
```

```python
# Vulkn q DataFrame
v.q('select name from system.tables limit 3 by database').s
```

```python
df = v.table('system.tables').select('database','name').limitBy(3, ('database',)).s
```

### fj (full-join) (right, keys, strictness=JoinStrictNess.All, global_mode=False)

- ```right``` - DataFrame - the right DataFrame to join on.
- ```keys``` - tuple(keys, ...) - the keys to use in the join condition.
- ```strictness``` - JoinStrictNess.(Any | All | AsOf | Default). Default - JoinStrictNess.All
- ```global_mode``` - Boolean value indicating whether to use GLOBAL mode. Default - False.

```sql
-- SQL
SELECT
    name
FROM system.tables
LIMIT 3 BY database
```

```python
# Vulkn q DataFrame
v.q('select name from system.tables limit 3 by database').s
```

```python
df = v.table('system.tables').select('database','name').limitBy(3, ('database',)).s
```

### aj (ASOF-join) (right, keys, global_mode=False)

- ```right``` - DataFrame - the right DataFrame to join on.
- ```keys``` - tuple(keys, ...) - the keys to use in the join condition.
- ```global_mode``` - Boolean value indicating whether to use GLOBAL mode. Default - False.

```sql
-- SQL
SELECT
    name
FROM system.tables
LIMIT 3 BY database
```

```python
# Vulkn q DataFrame
v.q('select name from system.tables limit 3 by database').s
```

```python
df = v.table('system.tables').select('database','name').limitBy(3, ('database',)).s
```

### cj (cross-join) (right, global_mode=False)

- ```right``` - DataFrame - the right DataFrame to join on.
- ```global_mode``` - Boolean value indicating whether to use GLOBAL mode. Default - False.

```sql
-- SQL
SELECT
    name
FROM system.tables
LIMIT 3 BY database
```

```python
# Vulkn q DataFrame
v.q('select name from system.tables limit 3 by database').s
```

```python
df = v.table('system.tables').select('database','name').limitBy(3, ('database',)).s
```

