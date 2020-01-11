Joins are implemented via the JoinDataFrame function. This function materializes the provided QueryString 
and SelectQuery DataFrames and returns a single SelectQueryDataFrame. You can call the JoinDataFrame 
directly however this approach is not recommended.

## Calling JoinDataFrame directly

### *vulkn.dataframe.JoinDataFrame(ctx, jointype, left, right, keys=None, strictness=JoinStrictness.All, global_mode=False)*

- **Parameters**
    - ```ctx``` - The Vulkn() context where the join query should occur.
    - ```jointype``` - JoinType.(Left | Right | LeftInner | RightInner | Inner | Join | LeftOuter | RightOuter | Full | FullOuter | Cross).
    - ```left``` - DataFrame - the left DataFrame to join. 
    - ```right``` - DataFrame - the right DataFrame to join.
    - ```keys``` - tuple(keys, ...) - the keys to use in the join condition.
    - ```strictness``` - JoinStrictNess.(Any | All | AsOf | Default). Default - JoinStrictNess.All
    - ```global_mode``` - Boolean value indicating whether to use GLOBAL mode. Default - False.
- **Returns**
    - ```vulkn.dataframe.SelectQueryDataFrame```
- **Examples**
        ```python
        from vulkn.dataframe import JoinDataFrame, JoinType, JoinStrictness

        v = Vulkn()
        l = v.table('system.databases').select('data_path',c('name').alias('database'))
        r = v.table('system.tables').select('database',c('name').alias('table_name'))
        
        df = JoinDataFrame(v, JoinType.Left, l, r, ('database',), strictness=JoinStrictness.Any, global_mode=True)
        df.show_sql()
        """SELECT * FROM (
            SELECT data_path, name AS database FROM system.databases
        ) GLOBAL ANY LEFT JOIN (
            SELECT database, name AS table_name FROM system.tables
        ) USING (database);"""
        ```

## DataFrame Join methods

### *join(jointype, right, keys, strictness=JoinStrictNess.All, global_mode=False)*

- **Parameters**
    - ```jointype``` - JoinType.(Left | Right | LeftInner | RightInner | Inner | Join | LeftOuter | RightOuter | Full | FullOuter | Cross).
    - ```right``` - DataFrame - the right DataFrame to join on. 
    - ```keys``` - tuple(keys, ...) - the keys to use in the join condition.
    - ```strictness``` - JoinStrictNess.(Any | All | AsOf | Default). Default - JoinStrictNess.All
    - ```global_mode``` - Boolean value indicating whether to use GLOBAL mode. Default - False.
- **Returns**
    - ```vulkn.dataframe.SelectQueryDataFrame```
- **Examples**
    * SQL
    ```sql
    SELECT 
        a.data_path, 
        b.database, 
        b.name AS table_name
    FROM system.databases AS a
    GLOBAL ANY LEFT JOIN system.tables AS b ON a.name = b.database
    ```
    * Raw Query
    ```python
    v.q("""
        select
            a.data_path,
            b.database,
            b.name as table_name
        from system.databases as a
        global any left join system.tables as b on a.name = b.database""").s
    ```
    * DataFrame
    ```python
    d = v.table('system.databases').select('data_path',c('name').alias('database'))
    t = v.table('system.tables').select('database',c('name').alias('table_name'))
    d.join(JoinType.Left, t, ('database',), strictness=JoinStrictness.Any, global_mode=True).s
    ```

### *ej (equi-join) (right, keys, strictness=JoinStrictNess.All, global_mode=False)*

- **Parameters**
    - ```right``` - DataFrame - the right DataFrame to join on.
    - ```keys``` - tuple(keys, ...) - the keys to use in the join condition.
    - ```strictness``` - JoinStrictNess.(Any | All | AsOf | Default). Default - JoinStrictNess.All
    - ```global_mode``` - Boolean value indicating whether to use GLOBAL mode. Default - False.
- **Returns**
    - ```vulkn.dataframe.SelectQueryDataFrame```
- **Examples**
    * SQL
    ```sql
    SELECT 
        a.data_path, 
        b.database, 
        b.name AS table_name
    FROM system.databases AS a
    INNER JOIN system.tables AS b ON a.name = b.database
    ```
    * Raw Query
    ```python
    v.q("""
        select
            a.data_path,
            b.database,
            b.name as table_name
        from system.databases as a
        join system.tables as b on a.name = b.database""").s
    ```
    * DataFrame
    ```python
    d = v.table('system.databases').select('data_path',c('name').alias('database'))
    t = v.table('system.tables').select('database',c('name').alias('table_name'))
    d.ej(t, ('database',)).s
    ```

### *rj (right-join) (left, keys, strictness=JoinStrictNess.All, global_mode=False)*

- **Parameters**
    - ```left``` - DataFrame - the left DataFrame to join on.
    - ```keys``` - tuple(keys, ...) - the keys to use in the join condition.
    - ```strictness``` - JoinStrictNess.(Any | All | AsOf | Default). Default - JoinStrictNess.All
    - ```global_mode``` - Boolean value indicating whether to use GLOBAL mode. Default - False.
- **Returns**
    - ```vulkn.dataframe.SelectQueryDataFrame```
- **Examples**
    * SQL
    ```sql
    SELECT 
        a.data_path, 
        b.database, 
        b.name AS table_name
    FROM system.databases AS a
    RIGHT JOIN system.tables AS b ON a.name = b.database
    ```
    * DataFrame
    ```python
    d = v.table('system.databases').select('data_path',c('name').alias('database'))
    t = v.table('system.tables').select('database',c('name').alias('table_name'))
    d.rj(t, ('database',)).s
    ```

### *lj (left-join) (right, keys, strictness=JoinStrictNess.All, global_mode=False)*

- **Parameters**
    - ```right``` - DataFrame - the right DataFrame to join on.
    - ```keys``` - tuple(keys, ...) - the keys to use in the join condition.
    - ```strictness``` - JoinStrictNess.(Any | All | AsOf | Default). Default - JoinStrictNess.All
    - ```global_mode``` - Boolean value indicating whether to use GLOBAL mode. Default - False.
- **Returns**
    - ```vulkn.dataframe.SelectQueryDataFrame```
- **Examples**
    * SQL
    ```sql
    SELECT 
        a.data_path, 
        b.database, 
        b.name AS table_name
    FROM system.databases AS a
    RIGHT JOIN system.tables AS b ON a.name = b.database
    ```
    * DataFrame
    ```python
    d = v.table('system.databases').select('data_path',c('name').alias('database'))
    t = v.table('system.tables').select('database',c('name').alias('table_name'))
    d.lj(t, ('database',)).s
    ```

### *fj (full-join) (right, keys, strictness=JoinStrictNess.All, global_mode=False)*

- **Parameters**
    - ```right``` - DataFrame - the right DataFrame to join on.
    - ```keys``` - tuple(keys, ...) - the keys to use in the join condition.
    - ```strictness``` - JoinStrictNess.(Any | All | AsOf | Default). Default - JoinStrictNess.All
    - ```global_mode``` - Boolean value indicating whether to use GLOBAL mode. Default - False.
- **Returns**
    - ```vulkn.dataframe.SelectQueryDataFrame```
- **Examples**
    * SQL
    ```sql
    SELECT 
        a.data_path, 
        b.database, 
        b.name AS table_name
    FROM system.databases AS a
    FULL JOIN system.tables AS b ON a.name = b.database
    ```
    * Raw Query
    ```python
    v.q('select name from system.tables limit 3 by database').s
    ```
    * DataFrame
    ```python
    d = v.table('system.databases').select('data_path',c('name').alias('database'))
    t = v.table('system.tables').select('database',c('name').alias('table_name'))
    d.fj(t, ('database',)).s
    ```

### *aj (ASOF-join) (right, keys, global_mode=False)*

- **Parameters**
    - ```right``` - DataFrame - the right DataFrame to join on.
    - ```keys``` - tuple(keys, ...) - the keys to use in the join condition.
    - ```global_mode``` - Boolean value indicating whether to use GLOBAL mode. Default - False.
- **Returns**
    - ```vulkn.dataframe.SelectQueryDataFrame```
- **Examples**
    * SQL
    ```sql
    SELECT
        a.*, b.*
    FROM (SELECT * FROM default.vector_example WHERE key = 1) AS a
    ASOF JOIN (SELECT * FROM default.vector_example WHERE key = 2) AS b
    USING (key)
    ```
    * DataFrame
    ```python
    key = ArrayVector.range(1,3).take(15).sort().cache().alias('key')
    timestamp = ArrayVector.rand(DateTime('2019-01-01 00:00:00'),DateTime('2019-01-01 23:59:59'),15).cast(DateTime).cache().alias('timestamp')
    metric = ArrayVector.rand(1,8192,15).cache().alias('metric')

    df = v.table.fromVector('default.vector_example', (key, timestamp, metric))
    sensor1 = df.select('timestamp', col('metric').alias('metric_1'), UInt8(0).alias('k')).where(c('key') == 1)
    sensor2 = df.select('timestamp', col('metric').alias('metric_2'), UInt8(0).alias('k')).where(c('key') == 2)
    sensor1.aj(sensor2, ('k','timestamp',)).select('timestamp', 'metric_1', 'metric_2').s

      row  timestamp              metric_1    metric_2
    -----  -------------------  ----------  ----------
        1  2019-01-01 19:04:11        4300         200
        2  2019-01-01 20:41:12        5163         200
        3  2019-01-01 07:45:29        3296        4482
        4  2019-01-01 13:04:16        3674        2905
        5  2019-01-01 10:22:29        3599        4482

    (5 rows)
    ```

### *cj (cross-join) (right, global_mode=False)*

- **Parameters**
    - ```right``` - DataFrame - the right DataFrame to join on.
    - ```global_mode``` - Boolean value indicating whether to use GLOBAL mode. Default - False.
- **Returns**
    - ```vulkn.dataframe.SelectQueryDataFrame```
- **Examples**
    * SQL
    ```sql
    SELECT 
        a.data_path, 
        b.database, 
        b.name AS table_name
    FROM system.databases AS a
    CROSS JOIN system.tables AS b
    ```
    * DataFrame
    ```python
    d = v.table('system.databases').select('data_path',c('name').alias('database'))
    t = v.table('system.tables').select('database',c('name').alias('table_name'))
    d.cj(t).s
    ```

## Join Functions

The following functions can be used to join multiple DataFrames.

### *vulkn.dataframe.aj(dataframes, keys, global_mode)*

- **Parameters**
    - ```dataframes``` - list - a list of dataframes to perform the ASOF join on.
    - ```keys``` - tuple(keys, ...) - the keys to use in the join condition. The last value in the 
    tuple is assumed to be the time or integer dimension used for the ASOF join. Other values are assumed
    to be key columns.
    - ```global_mode``` - Boolean value indicating whether to use GLOBAL mode. Default - False.
- **Returns**
    - ```vulkn.dataframe.SelectQueryDataFrame```
- **Examples**
    * DataFrame
    ```python
    devices = []
    for i in range(0,5):
        devices.append(v
            .table('timeseries')
            .select(UInt8(1).alias('id'), 'ts', c('value').alias('device-'+str(i)))
            .where("key='device-{device:UInt64}'")
            .params({'device': i}).cache())

    from vulkn.dataframe import aj

    df = aj(devices, ('id', 'ts'))
    df.limit(30).s
    ```
---
