## Working with parameters

All DataTables support parameters through standard ClickHouse parameterized queries embedded in the 
query string, column expression or variable or data type. Python types are implicitly converted/formatted
as required.

```python
>>> df = v.q('select database, name from system.tables where database = {database:String}')
>>> df2 = v.table('system.tables').select(col('{database:String}').alias('datname'), 'name').where('database = {database:String}')
```

The underlying SQL created by the DataTable can be viewed using show_sql method.

```python
>>> df.show_sql()
'SELECT database, name FROM system.tables WHERE database = {database:String};'
>>> df2.show_sql()
'SELECT {database:String} AS datname, name FROM system.tables WHERE database = {database:String};
```

You can pass the parameters as key/value pairs to the show_sql method:

```python
>>> df.show_sql(database='system')
"SELECT database, name FROM system.tables WHERE database = 'system';"
```

---

## Query Execution

Each DataTable type supports an ```exec``` method that immediately executes the DataTable. The ```exec```
method returns a RecordSet object containing the raw query result. ```exec``` can also accept any 
parameters. This will be rendered into the final SQL before execution.

---

### *exec(\*\*params)*, *e*

* Aliases: ```e```
* Parameters:
    * ```params``` - **kwargs style key/value argument
* Returns: vulkn.recordset.RecordSet
* Examples:
    ```python
    df = (v
        .table('system.tables')
        .select(col('{database:String}').alias('datname'), 'name')
        .where('database = {database:String}')
        .limit(1))
    df.e(database='system')
    <vulkn.recordset.RecordSet object at 0x7f4af91e8c50>
    ```
---

### *show()*, *s*

* Description: Pretty prints a recordset object to the console.
* Aliases: ```s```
* Returns: str
* Examples:
    ```python
    df = v.table('system.tables').select('database', 'name').where("database = 'system'").limit(1))
    df.show()

      row  datname    name
    -----  ---------  ------------------------------
        1  system     aggregate_function_combinators

    (1 row)
    ```

    s can also be called as an attribute
    ```python
    df.e(database='system').s

      row  datname    name
    -----  ---------  ------------------------------
        1  system     aggregate_function_combinators

    (1 row)
    ```
    If no parameters are specified s can be called on the DataTable object itself.
    ```python
    df.s
    ```
---

### *to_records()*, *r*

* Description: Executes and returns the DataTable/raw query result as a list of dictionary records. 
Note this proxies the to_records call through to the underlying RecordSet object.
* Aliases: ```r```
* Returns: list of dictionaries/records
* Example:
    ```python
    >>> df = (v.table('system.tables').select('database', 'name').where("database = 'system'").limit(3))
    >>> df.exec().to_records()
    [{'database': 'system', 'name': 'aggregate_function_combinators'},
    {'database': 'system', 'name': 'asynchronous_metrics'},
    {'database': 'system', 'name': 'build_options'}]
    >>> df.r
    [{'database': 'system', 'name': 'aggregate_function_combinators'},
    {'database': 'system', 'name': 'asynchronous_metrics'},
    {'database': 'system', 'name': 'build_options'}]
    ```
---

### *to_pandas()*, *p*

* Description: Executes and returns the DataTable/raw query result as a Pandas DataTable. 
Note this proxies the to_records call through to the underlying RecordSet object.
* Aliases: ```p```
* Returns: Pandas DataTable
* Example:
    ```python
    >>> df = (v.table('system.tables').select('database', 'name').where("database = 'system'").limit(3))
    >>> df.e().to_pandas()
    database                            name
    0   system  aggregate_function_combinators
    1   system            asynchronous_metrics
    2   system                   build_options
    >>> df.p
    database                            name
    0   system  aggregate_function_combinators
    1   system            asynchronous_metrics
    2   system                   build_options
    ```
---

## Caching

DataTables can be cached using a call to ```cache```. Cache will create a temporary/Vulkn managed 
object stored using the specified engine. To use parameters with cache you must use call ```params```
before the ```cache``` call. Note that only SelectQueryDataTables support parameterized caching.
---

### *params(\*\*params)*

* Parameters
    * ```**params``` - a dictionary/**kwargs style key/value list of parameters
* Description: Sets the parameters of the DataTable for use by a call to ```cache()```
* Returns: ```vulkn.datatable.SelectQueryDataTable```
---

### *cache(engine=None)*

Executes the DataTable/query and caches the result on the ClickHouse server. By limiting execution and 
storage/caching to ClickHouse users can very quickly analyze data and build comprehensive models. All
cached data is automatically destroyed at the end of the Vulkn session.

* Parameters:
    * ```engine=None``` - a valid ClickHouse engine object (see vulkn.engines). ```engines.Memory()``` 
    if not specified.
* Description: Sets the parameters of the DataTable for use by a call to ```cache()```
* Returns: ```vulkn.datatable.SelectQueryDataTable```
* Examples:
    ```python
    >>> vulkn.session.log.setLevel('SQL')
    >>> df = v.table('system.tables').select('database', 'name').where("database = {database:String}").limit(3)
    >>> cached_df = df.params({'database': 'system'}).cache()
    2020-01-10 22:24:45,595 - root - SQL - DROP TABLE IF EXISTS vulkn.session_0a7a4cf4727a40d6a801b1dd21bdb320_v_8d8dc7925579b797bf414481a51f82fb;
    2020-01-10 22:24:45,643 - root - SQL - CREATE TABLE vulkn.session_0a7a4cf4727a40d6a801b1dd21bdb320_v_8d8dc7925579b797bf414481a51f82fb ENGINE = Memory() AS SELECT database, name FROM system.tables WHERE database = 'system' LIMIT 3;
    >>> cached_df.s
    2020-01-10 22:24:55,939 - root - SQL - SELECT * FROM vulkn.session_0a7a4cf4727a40d6a801b1dd21bdb320_v_8d8dc7925579b797bf414481a51f82fb;

    row  database    name
    -----  ----------  ------------------------------
        1  system      aggregate_function_combinators
        2  system      asynchronous_metrics
        3  system      build_options

    (3 rows)

    >>> cached_df.show_sql()
    'SELECT * FROM vulkn.session_0a7a4cf4727a40d6a801b1dd21bdb320_v_8d8dc7925579b797bf414481a51f82fb;'
    >>> 
    2020-01-10 22:25:03,296 - root - INFO - Purging cache...
    2020-01-10 22:25:03,314 - root - SQL - DROP TABLE IF EXISTS vulkn.session_0a7a4cf4727a40d6a801b1dd21bdb320;
    2020-01-10 22:25:03,371 - root - SQL - DROP TABLE IF EXISTS vulkn.session_0a7a4cf4727a40d6a801b1dd21bdb320_v_8d8dc7925579b797bf414481a51f82fb;
    Exit code 0
    Logging trace to /tmp/ironman-1755e5f8-7f6c-444b-b2a5-dae94e8f40f9/logs/clickhouse-server.log
    Logging errors to /tmp/ironman-1755e5f8-7f6c-444b-b2a5-dae94e8f40f9/logs/clickhouse-server.err.log
    Include not found: networks
    Include not found: networks
    ```
---
