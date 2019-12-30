# numbers

ClickHouse reference:
[numbers table function](https://clickhouse.yandex/docs/en/query_language/table_functions/numbers/)
, [system.numbers](https://clickhouse.yandex/docs/en/operations/system_tables/#system-numbers)
, [system.numbers_mt](https://clickhouse.yandex/docs/en/operations/system_tables/#system-numbers-mt)

- ```count``` - the number of sequential integers to return starting from 1.
- ```system``` - whether to use the 'system.numbers' table to generate values. Default ```False```.
- ```mt``` - whether to use the multi-threaded table function or system table variants. Default ```False```.


```vulkn.one()``` is a simple DataFrame equivalent to the SQL statement:

```sql
SELECT dummy FROM system.one
```

It mimics behaviour found in some other databases (with a 'DUAL' table).

## Example

```python
v.one().s

  row    dummy
-----  -------
    1        0

(1 row)

v.one().select('*').s

  row    dummy
-----  -------
    1        0

(1 row)

```
