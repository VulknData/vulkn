## *vectorize_by(key, [non-key-columns, ..,] sort)*

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