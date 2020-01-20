# Operators

Vulkn supports all ClickHouse operators using either raw SQL, column expressions, column literals 
or pure Python mechanisms.

## Using Operators

### Raw SQL

```python
>>> v.q("SELECT database, name FROM system.tables WHERE database = 'system' LIMIT 3").s

  row  database    name
-----  ----------  ------------------------------
    1  system      aggregate_function_combinators
    2  system      asynchronous_metrics
    3  system      build_options

(3 rows)
```

### Column Expressions

```python
>>> v.table('system.tables').select('database', 'name').where("database = 'system'").limit(3).s

  row  database    name
-----  ----------  ------------------------------
    1  system      aggregate_function_combinators
    2  system      asynchronous_metrics
    3  system      build_options

(3 rows)
```

### Column Literals

```python
>>> v.table('system.tables').select('database', 'name').where(c("database = 'system'")).limit(3).s

  row  database    name
-----  ----------  ------------------------------
    1  system      aggregate_function_combinators
    2  system      asynchronous_metrics
    3  system      build_options

(3 rows)
```

### Python

Python operators can be used within any method and will be automatically converted to SQL providing 
one of the variables is a Vulkn declared type or column literal.

```python
ss = 'substring(database, 3)'
l = c('upper(name)').cast(String).length().alias('ucase_name')
v.table('system.tables').select(ss, l).where(c('database') == 'system').limit(3).s

  row  substring(database, 3)      ucase_name
-----  ------------------------  ------------
    1  stem                                30
    2  stem                                20
    3  stem                                13

(3 rows)
```

## Available Operators

### Arithmetic Operators

Description | ClickHouse Operator | Vulkn Python | Examples
-- | -- | -- | --
addition, concatentation | + | + | ```v.q('SELECT 1 + 1').s```<br/>```v.select(vU8(1) + 1).s```<br/>```v.select(c(1).cast(UInt8) + 1).s```
subtraction | - | - | ```v.q('SELECT 1 - 1').s```<br/>```v.select(vU8(1) - 1).s```<br/>```v.select(c(1).cast(UInt8) - 1).s```
multiplication | * | * | ```v.q('SELECT 2 * 2').s```<br/>```v.select(vU8(2) * 2).s```<br/>```v.select(c(2).cast(UInt8) * 1).s```
division (float) | / | / | ```v.q('SELECT 2 / 2').s```<br/>```v.select(vU8(2) / 2).s```<br/>```v.select(c(2).cast(UInt8) / 2).s```
division (floor) | intDiv (function) | // | ```v.q('SELECT 5 // 3').s```<br/>```v.select(vU8(5) // 3).s```<br/>```v.select(c(5).cast(UInt8) // 3).s```
modulus | % | % | ```v.q('SELECT 5 % 3').s```<br/>```v.select(vU8(5) % 3).s```<br/>```v.select(c(5).cast(UInt8) % 3).s```

### Comparison Operators

Description | ClickHouse Operator | Vulkn Python | Examples
-- | -- | -- | --
equals | =<br/>== | ==<br/>eq<br/>equals | ```v.q('SELECT 1 == 1').s```<br/>```v.q('SELECT 1 = 1').s```<br/>```v.select(vU8(1) == 1).s```<br/>```v.select(c(1) == 1).s```<br/>```v.select(vU8(1).eq(1)).s```<br/>```v.select(c(1).equals(1)).s```
not equals | !=<br/><> | !=<br/>ne<br/>notEquals<br/>not_equals | ```v.q('SELECT 1 != 1').s```<br/>```v.select(vU8(1) != 1).s```<br/>```v.select(c(1) != 1).s```<br/>```v.select(vU8(1).ne(1)).s```<br/>```v.select(c(1).notEquals(1)).s```
greater than | > | ><br/>gt<br/>greater | ```v.q('SELECT 1 > 2').s```<br/>```v.select(vU8(1) > 2).s```<br/>```v.select(c(1) > c(2)).s```<br/>```v.select(vU8(1).gt(2)).s```<br/>```v.select(c(1).greater(c(2))).s```
less than | < | <<br/>lt<br/>less | ```v.q('SELECT 1 < 1').s```<br/>```v.select(vU8(1) < 2).s```<br/>```v.select(c(1) < 2).s```<br/>```v.select(vU8(1).lt(2)).s```<br/>```v.select(c(1).less(2)).s```
greater than or equal to | >= | >=<br/>greaterOrEquals<br/>greater_or_equals | ```v.q('SELECT 1 >= 2').s```<br/>```v.select(vU8(1) >= 2).s```<br/>```v.select(c(1) >= 2).s```<br/>```v.select(c(1).greaterOrEquals(2)).s```
less than or equal to | <= | <=<br/>lessOrEquals<br/>less_or_equals | ```v.q('SELECT 1 <= 2').s```<br/>```v.select(vU8(1) <= 2).s```<br/>```v.select(c(1) <= 2).s```<br/>```v.select(c(1).lessOrEquals(2)).s```

### Logical Operators

Description | ClickHouse Operator | Vulkn Python | Examples
-- | -- | -- | --
logical and | AND | and_<br/>funcs.and_ | ```v.q('SELECT 1 AND 1').s```<br/>```v.select(c(1).and_(1)).s```<br/>```v.select(funcs.and_('col1 = 3', 'col2 = 4', String(n='baz') == 'foo')).s```
logical or | OR | or_<br/>funcs.or_ | ```v.q('SELECT 1 OR 1').s```<br/>```v.select(c(1).or_(1)).s```<br/>```v.q("SELECT (col1 = 3 AND col2 = 4) OR baz = 'foo'").s```<br/>```v.select(funcs.or_(funcs.and_('col1 = 3', 'col2 = 4'), String(n='baz') == 'foo'))).s```
logical not | NOT | not_<br/>funcs.not_ | ```v.q('SELECT NOT 1').s```<br/>```v.select(c(1).not_()).s```<br/>```v.select(funcs.not_('col1 = 3')).s```

### Bitwise Operators

Numeric types also support bitwise operations

Description | ClickHouse Operator | Vulkn Python | Examples
-- | -- | -- | --
bitwise and | bitAnd (function) | bitAnd<br/>bit_and<br/>& | ```v.q('SELECT bitAnd(1, 4)').s```<br/>```v.select(vU8(1).bitAnd(4)).s```<br/>```v.select(c(1).cast(UInt8) & 4).s```
bitwise or | bitOr (function) | bitOr<br/>bit_or<br/>\| | ```v.q('SELECT bitOr(1, 4)').s```<br/>```v.select(vU8(1).bitOr(4)).s```<br/>```v.select(c(1).cast(UInt8) | 4).s```
btiwise not | bitNot (function) | bitNot<br/>bit_not<br/>~ | ```v.q('SELECT bitNot(3)').s```<br/>```v.select(vU8(3).bitNot()).s```<br/>```v.select(~(c(3).cast(UInt8))).s```
bitwise xor | bitXor (function) | bitXor<br/>bit_xor<br/>^ | ```v.q('SELECT bitXor(3, 1)').s```<br/>```v.select(vU8(3).bitXor(1)).s```<br/>```v.select(c(3).cast(UInt8)^1).s```
bitwise left shift | bitShiftLeft (function) | bitShiftLeft<br/><< | ```v.q('SELECT bitShiftLeft(3748362, 3)').s```<br/>```v.select(vU32(3748362)<<3).s```<br/>```v.select(c(3748362).cast(UInt32)<<3).s```
bitwise right shift | bitShiftRight (function) | bitShiftRight<br/>>> | ```v.q('SELECT bitShiftRight(87651, 2)').s```<br/>```v.select(vU32(87651)>>2).s```<br/>```v.select(c(87651).cast(UInt32)>>2).s```

### Set Membership

Sets can be compared using the in_ and not_in_ set membership tests.

Description | ClickHouse Operator | Vulkn Python | Examples
-- | -- | -- | --
exists in set | [GLOBAL] IN | in_<br/>global_in_<br/>global_in | ```v.q('SELECT number FROM numbers(10) WHERE number IN (1, 4)').s```<br/>```v.numbers(10).select('*').where(c('number').in_(v.numbers(5))).s```
not in set | [GLOBAL] NOT IN | not_in_<br/>not_in<br/>global_not_in_<br/>global_not_in | ```v.q('SELECT number FROM numbers(10) WHERE number GLOBAL NOT IN (1, 4)').s```<br/>```v.numbers(10).select('*').where(c('number').global_not_in(v.numbers(5))).s```

### Range Testing

Description | ClickHouse Operator | Vulkn Python | Examples
-- | -- | -- | --
between inclusive | x BETWEEN x1 AND x2 | between<br/>bt | ```v.one().select(c(11).between(11, 24)).s```<br/>```v.one().select(c(11).bt(11, 24)).s```
not_between inclusive | x NOT BETWEEN x1 AND x2 | not_between<br/>notBetween<br/>nbt | ```v.one().select(c(11).not_between(11, 24)).s```<br/>```v.one().select(c(11).nbt(11, 24)).s```

### Null Handling

Description | ClickHouse Operator | Vulkn Python | Examples
-- | -- | -- | --
is null | isNull | is_null<br/>isn<br/>isNull | ```v.select(String('hello').is_null()).s```
is not null  | isNotNull | is_not_null<br/>isnn<br/>isNotNull | ```v.select(NULL.isnn()).s```
cast to not null(type) | assumeNotNull | assume_not_null<br/>nn | ```v.select(String('hello').nn()).s```
cast to null(type) | toNullable | to_nullable<br/>tn<br/>toNullable | ```v.select(String('hello').to_nullable()).s```