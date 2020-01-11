# DataFrames

DataFrames are specialised container objects that can refer to either tables or queries including 
queries comprised of other DataFrames or tables in the form of subselects and joins. Vulkn provides 
a number of DataFrame entrypoints. All DataFrame variants are compatible and can be used in joins, 
for creating cache tables or creating new tables, relations and vectors.

By default DataFrames are executed 'lazily'. This means that they are only executed when a result is
requested. Parameters and caching are also supported to enable re-use and acceleration.

The following provides an overview of the available entrypoints. Please see the Reference section
for more detail.



## Entrypoints

### q

A simple SQL string interface. Mostly identical in behavior to issuing queries via the clickhouse-client CLI

```python
>>> v.q('select count() from system.tables').s 

  row    count()
-----  ---------
    1         40

(1 row)
```

### table, select

An ORM interface similar to those found within other BigData frameworks.

```python
>>> pprint.pprint(v.table('system.tables').all().limit(1).r)
[{'create_table_query': nan,
  'data_paths': '[]',
  'database': 'system',
  'dependencies_database': '[]',
  'dependencies_table': '[]',
  'engine': 'SystemAggregateFunctionCombinators',
  'engine_full': nan,
  'is_temporary': 0,
  'metadata_modification_time': '0000-00-00 00:00:00',
  'metadata_path': '/tmp/ironman-5cb7f7dc-d45b-443d-bd9c-2a25aa0b077a/clickhouse/metadata/systemaggregate_function_combinators.sql',
  'name': 'aggregate_function_combinators',
  'partition_key': nan,
  'primary_key': nan,
  'sampling_key': nan,
  'sorting_key': nan,
  'storage_policy': nan}]
```

### one

Table function interface to system.one.

```python
>>> v.one()
<vulkn.dataframe.SelectQueryDataFrame object at 0x7f5ee84b2da0>
>>> v.one().s

  row    dummy
-----  -------
    1        0

(1 row)
```

### numbers

Generates a sequence of numbers via the system.numbers, system.numbers_mt tables and the table 
functions numbers(), numbers_mt().

```python
>>> v.numbers(100).exec().to_list()
[(0,), (1,), (2,), (3,), (4,), (5,), (6,), (7,), (8,), (9,)]
```

### range

Variant on the numbers DataFrame that allows negative start/end positions.

```python
>>> v.range(-3,3).s

  row    range
-----  -------
    1       -3
    2       -2
    3       -1
    4        0
    5        1
    6        2
    7        3

(7 rows)

>>> v.range(3,9).select(funcs.agg.sum(c('range'))).s

  row    sum(range)
-----  ------------
    1            42

(1 row)
```

### random, randfloat

Generates random 64 bit integers within the prescribed range. The ```randfloat``` variant generates 
a Float64 type.

```python
>>> v.random(5, start=0, end=5).s

  row    number
-----  --------
    1         3
    2         5
    3         2
    4         2
    5         4

(5 rows)
```

## Others

### update

Many BigData or timeseries systems require rewriting entire datasets or partitions. ClickHouse permits 
updates and deletes for non-key columns.

!!! TODO
    Documentation is incomplete.

### delete

Many BigData or timeseries systems require rewriting entire datasets or partitions. ClickHouse permits 
updates and deletes for non-key columns.

!!! TODO
    Documentation is incomplete.

### data

Data is a special dunder dictionary that automatically maps databases and tables under a dictionary-like 
interface. Each database.table is mapped to a key/value pair with the values/object represented by a BaseTableDataFrame object.

#### Examples

* Listing all tables by key
```python
>>> pprint.pprint(list(v.data.keys())[:5])
['system.aggregate_function_combinators',
 'system.asynchronous_metrics',
 'system.build_options',
 'system.clusters',
 'system.collations']
```

* Values as BaseTableDataFrames
```python
>>> pprint.pprint(list(v.data.values())[:5])
[<vulkn.dataframe.BaseTableDataFrame object at 0x7f5ee84b2630>,
 <vulkn.dataframe.BaseTableDataFrame object at 0x7f5ee8456198>,
 <vulkn.dataframe.BaseTableDataFrame object at 0x7f5eb8b4f5f8>,
 <vulkn.dataframe.BaseTableDataFrame object at 0x7f5ee845d978>,
 <vulkn.dataframe.BaseTableDataFrame object at 0x7f5ee84b85f8>]
```

* Using the data object in queries.

```python
>>> v.data['system.tables'].select('count()').exec().to_list()
[(44,)]
```

* DataFrames can also be created from nested properties of the data dictionary.

```python
>>> v.data.system.tables.count().s

  row    count()
-----  ---------
    1         44

(1 row)
```