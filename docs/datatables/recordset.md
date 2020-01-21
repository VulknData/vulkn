Query results are returned as a ```vulkn.recordset.RecordSet``` object. RecordSets provide many methods for marshalling the
data from a ClickHouse result to a Python friendly format.

## *show, s*

* Description: Provides a pretty print SQL table view of the DataTable result.
* Returns: ```str```
* Example:
    ```python
    v.table('system.tables').all().head(3).exec().s
    ```
---

## *show_pandas(num_rows=50)*

* Description: Provides a Pandas DataFrame view of the DataTable result.
* Returns: ```str```
* Example:
    ```python
    >>> v.table('system.tables').all().head(3).exec().show_pandas()
        database                            name  ... sampling_key  storage_policy
    0   system  aggregate_function_combinators  ...          NaN             NaN
    1   system            asynchronous_metrics  ...          NaN             NaN
    2   system                   build_options  ...          NaN             NaN

    [3 rows x 16 columns]
    ```
---

## *len()*

* Description: Returns the length of the DataTable result.
* Returns: ```int```
* Example:
    ```python
    >>> len(v.table('system.tables').all().head(3).exec())
    3
    ```
---

## *columns*

* Description: Returns a list of columns in the DataTable result.
* Returns: ```list(str)```
* Example:
    ```python
    v.table('system.tables').all().head(3).exec().columns
    ['database', 'name', 'engine', 'is_temporary', 'data_paths', 'metadata_path', 
    'metadata_modification_time', 'dependencies_database', 'dependencies_table', 
    'create_table_query', 'engine_full', 'partition_key', 'sorting_key', 'primary_key', 
    'sampling_key', 'storage_policy']
    ```
---

## *chtypes*

* Description: Returns a list of ClickHouse types for the DataTable result.
* Returns: ```list(str)```
* Example:
    ```python
    v.table('system.tables').all().head(3).exec().chtypes
    ['String', 'String', 'String', 'UInt8', 'Array(String)', 'String', 'DateTime', 'Array(String)',
    'Array(String)', 'String', 'String', 'String', 'String', 'String', 'String', 'String']
    ```
---

## *pytypes*

* Description: Returns a list of Python types for the DataTable result.
* Returns: ```list(str)```
* Example:
    ```python
    v.table('system.tables').all().head(3).exec().pytypes
    [<class 'str'>, <class 'str'>, <class 'str'>, <class 'int'>, <class 'object'>, <class 'str'>, 
    <class 'datetime.datetime'>, <class 'object'>, <class 'object'>, <class 'str'>, <class 'str'>, 
    <class 'str'>, <class 'str'>, <class 'str'>, <class 'str'>, <class 'str'>]
    ```
---

## *pdtypes*

* Description: Returns a list of Pandas types for the DataTable result.
* Returns: ```list(str)```
* Example:
    ```python
    v.table('system.tables').all().head(3).exec().pdtypes
    {'is_temporary': dtype('uint8'), 'metadata_modification_time': dtype('<M8')}
    ```
---

## *to_records, r*

* Description: Returns the result as a list of key/value pair dictionary/records.
* Returns: ```list(dict)```
* Example:
    ```python
    v.table('system.tables').all().head(3).select('database','name').exec().r
    [{'database': 'system', 'name': 'aggregate_function_combinators'},
     {'database': 'system', 'name': 'asynchronous_metrics'},
     {'database': 'system', 'name': 'build_options'}]
    ```
---

## *to_pandas, p*

* Description: Returns the result as a Pandas DataFrame.
* Returns: ```Pandas DataFrame```
* Example:
    ```python
    v.table('system.tables').all().head(3).select('database','name').exec().p
      database                            name
    0   system  aggregate_function_combinators
    1   system            asynchronous_metrics
    2   system                   build_options
    ```
---

## *to_dict, d*

* Description: Returns the result as a list of key/value pair dictionary/records.
* Returns: ```list(dict)```
* Example:
    ```python
    v.table('system.tables').all().head(3).select('database','name').exec().d
    [{'database': 'system', 'name': 'aggregate_function_combinators'},
     {'database': 'system', 'name': 'asynchronous_metrics'},
     {'database': 'system', 'name': 'build_options'}]
    ```
---

## *to_list, l*

* Description: Returns the result as a list of tuples.
* Returns: ```list(tuple)```
* Example:
    ```python
    v.table('system.tables').all().head(3).select('database','name').exec().l
    [('system', 'aggregate_function_combinators'),
     ('system', 'asynchronous_metrics'),
     ('system', 'build_options')]
    ```
---

## *to_recarray, n*

* Description: Returns the result as a NumPy ndarray.
* Returns: ```numpy ndarray```
* Example:
    ```python
    v.table('system.tables').all().head(3).select('database','name').exec().n
    rec.array([('system', 'aggregate_function_combinators'),
            ('system', 'asynchronous_metrics'),
            ('system', 'build_options')],
            dtype=[('database', 'O'), ('name', 'O')])
    ```
---
