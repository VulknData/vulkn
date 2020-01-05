# UUID

ClickHouse reference - [UUID functions](https://clickhouse.yandex/docs/en/query_language/functions/uuid_functions/)

## Creation

### UUID.generateUUIDv4, UUID.UUIDv4

Returns a new v4 UUID.

```python
v.s(UUID.UUIDv4())
'c735a549-ba27-4cb3-94c4-f795ebb3f524'
```

## Methods

### UUIDStringToNum

```python
v.select(UUID('fe74651b-3fc2-44cc-92b3-5a975dc22f13').UUIDStringToNum().cast(String).base64Encode()).s

  row  base64Encode(cast(UUIDStringToNum(\'fe74651b-3fc2-44cc-92b3-5a975dc22f13\'), \'String\'))
-----  -------------------------------------------------------------------------------------------
    1  /nRlGz/CRMySs1qXXcIvEw==

(1 row)
```

### UUIDNumToString

```python
v.select(UUID(UUID('fe74651b-3fc2-44cc-92b3-5a975dc22f13').UUIDStringToNum()).UUIDNumToString()).s

  row  UUIDNumToString(UUIDStringToNum(\'fe74651b-3fc2-44cc-92b3-5a975dc22f13\'))
-----  ----------------------------------------------------------------------------
    1  fe74651b-3fc2-44cc-92b3-5a975dc22f13

(1 row)
```