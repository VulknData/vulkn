# Data Types

ClickHouse supports numerous data types including Integers, Floats, Decimals, Bools, Strings, UUIDs,
DateTime, Array, Tuples, AggregateFunctions, nested structures and more.

As ClickHouse is a strongly typed datastore, Vulkn attempts to map existing Python datatypes to 
ClickHouse datatypes in a similar manner to an ORM. Vulkn also allows for creating additional datatypes
the make it easier to work with ClickHouse from the Python eco-system.

## ClickHouse references

* [Data Types](https://clickhouse.yandex/docs/en/data_types/)

## Variables

Variables are declared and assigned using normal Python notation:

```python
x = Int8(34)
s = String('Hello World!')
```

Once declared you can use most variables as you would Python types and then use them within queries:

```python
s = String('Hello world  ')
s = s.strip()
l = s.len()
v.select(s.alias('stripped string'), l.alias('length')).s

  row  stripped string      length
-----  -----------------  --------
    1  Hello world              13

(1 row)
```

Typed variables also allow datatypes to propagate through their respective method calls

```python
v.select(s.typename().alias('stripped string'), l.typename().alias('length')).s

  row  stripped string    length
-----  -----------------  --------
    1  String             UInt64

(1 row)
```

You can view the generated SQL at any time either by printing the individual variable using the print 
statement or using the ```.show_sql()``` method of a DataFrame:

```python
v.select(s.typename().alias('stripped string'), l.typename().alias('length')).show_sql()
"""SELECT
    toTypeName(replaceRegexpAll('Hello world  ', '^s*|s*$', '')) AS `stripped string`,
    toTypeName(length(replaceRegexpAll('Hello world  ', '^s*|s*$', ''))) AS length;"""
```

Existing variables and columns can also be declared using ```<Type>(name='')``` (or ```<Type>(n='')```). 
This allows use of the object/datatype type system by name rather than by value.

For example:

```python
database = String(n='database')
tablename = String(n='name')
v.table('system.tables').select(database, tablename).limit(3).s

  row  database           name
-----  -----------------  --------------
    1  cached             test
    2  cached             test1
    3  database_for_dict  table_for_dict

(3 rows)
```

## Available Types

Family | ClickHouse Data Type | Range | Vulkn Data Type | Vulkn Shortcut | Examples |
-- | -- | -- | -- | -- | -- |
Integer | Int8 | [-128, 127] | Int8 | vI8 | ```x = Int8(34)```, ```v.select(c(34).cast(Int8)).r```, ```x = vI8(34)```
Integer | Int16 | [-32768, 32767] | Int16 | vI16 | ```x = Int16(3445)```, ```v.select(c(3445).cast(Int16)).r```
Integer | Int32 | [-2147483648, 2147483647] | Int32 | vI32 | ```x = Int32(545678)```, ```v.select(c(545678).cast(Int32)).r```
Integer | Int64 | [-9223372036854775808, 9223372036854775807] | Int64 | vI64 | ```x = vI64(3372036854775)```, ```v.select(c(3372036854775).cast(Int64)).r```
Integer | UInt8 | [0, 255] | UInt8 | vU8 | ```x = UInt8(34)```, ```v.select(c(34).cast(UInt8)).r```
Integer | UInt16 | [0, 65535] | UInt16 | vU16 | ```x = UInt16(3445)```, ```v.select(c(3445).cast(UInt16)).r```
Integer | UInt32 | [0, 4294967295] | UInt32 | vU32 | ```x = UInt32(545678)```, ```v.select(c(545678).cast(UInt32)).r```
Integer | UInt64 | [0, 18446744073709551615] | UInt64 | vU64 | ```x = UInt64(3372036854775)```, ```v.select(c(3372036854775).cast(UInt64)).r```
Float | Float, Float32 | [3.40282e+38, 3.40282e+38] | Float32 | vF32 | ```x = Float32(567.34)```, ```v.select(c(567.34).cast(Float32)).r```
Float | Float64 | [-1.79769e+308, 1.79769e+308] | Float64 | vF64 | ```x = Float64(567.34)```, ```v.select(c(567.34).cast(Float64)).r```
String | String | - | String | vS | ```x = String('hello world')```, ```v.select(c('hello world').cast(String)).r```
String | - | - | URL | vU | ```x = URL('https://www.yandex.ru')```
DateTime | Date | ['0000-00-00', '2106-02-07'] | Date | vD | ```x = Date('2019-01-01')```
DateTime | DateTime | ['0000-00-00 00:00:00', '2106-02-07 17:28:15'] | DateTime | vDT, vDT32 | ```x = DateTime('2106-02-07 17:28:15')```
Array | Array | - | Array | vA | ```x = Array([1,2,3])```

## DataFrame methods

Most methods within a DataFrame allow for any combination of typed variables, column names (strings), 
column expressions (strings) or column literals.

### Column Names

Column names are simple string names.

```python
v.table('system.tables').select('database', 'name').limit(3).s

  row  database           name
-----  -----------------  --------------
    1  cached             iot_car_inbound
    2  cached             iot_car_outbound
    3  dict_store         number_plate_lookup

(3 rows)
```

### Column Expressions

Column expressions are simple strings that allow you to specify the entire column formula/function as 
you would within a standard SQL statement. This can be applied to any method.

```python
v.table('system.tables').select('substring(database, 3)', 'upper(name)').where("database = 'system'").limit(3).s

  row  substring(database, 3)    upper(name)
-----  ------------------------  ------------------------------
    1  stem                      AGGREGATE_FUNCTION_COMBINATORS
    2  stem                      ASYNCHRONOUS_METRICS
    3  stem                      BUILD_OPTIONS

(3 rows)
```

### Column Literals

Column literals enable users to mix and match a literal SQL string with the type system. Use the 
functions ```c``` or ```col``` to declare a column literal.

```python
ss = 'substring(database, 3)'
l = c('upper(name)').cast(String).length().alias('ucase_name')
v.table('system.tables').select(ss, l).where("database = 'system'").limit(3).s

  row  substring(database, 3)      ucase_name
-----  ------------------------  ------------
    1  stem                                30
    2  stem                                20
    3  stem                                13

(3 rows)
```

### Operators

Python operators can be used within any method and will be automatically converted to SQL providing 
one of the variables is a Vulkn declared type or column literal.

```python
v.table('system.tables').select(ss, l).where(c('database') == 'system').limit(3).s

  row  substring(database, 3)      ucase_name
-----  ------------------------  ------------
    1  stem                                30
    2  stem                                20
    3  stem                                13

(3 rows)
```

### Mixing Python variables

Most Python variables, except dictionaries, can be mixed with most Vulkn variables and will be 
converted to the correct SQL type or a literal constant at query time.

Arrays, tuples, strings, integers, floats and datetime types can all be use within Vulkn:

```python
>>> v.select(list(range(0,10)), ('a','b'), ['my','array']).s

  row  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]    tuple(\'a\', \'b\')    [\'my\', \'array\']
-----  --------------------------------  ---------------------  ---------------------
    1  [0,1,2,3,4,5,6,7,8,9]             ('a','b')              ['my','array']

(1 row)
```

Dictionaries will be supported in the future as variants of the JSON data type and the JoinStorage 
table type.