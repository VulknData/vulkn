# one

ClickHouse reference - [system.one](https://clickhouse.yandex/docs/en/operations/system_tables/#system-one)

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
