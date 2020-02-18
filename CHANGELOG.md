## VULKИ release 19.0.6, 2020-02-18

### New Features

- Allow loading an entire table or parts of a table into memory using v.table('').load(). See http://docs.vulkndata.io/datatables/reference/#loadparts.
- Allow turning off query parsing / rewriting with the vulkn.session.enable_parser session variable. Can speed up parsing with large queries that don't require rewriting.

### Improvements

- Improved subquery generation for chained clauses of the same type. Also track clause usage in DataTables and automatically generate subqueries.
- VECTORIZE BY vectorX functions no longer require aliases.
- VECTORIZE BY no longer requires vector columns to be specified as separate columns.
- Allow expression columns in VECTORIZE BY statements.
- v.s() now attempts a literal eval on the returned row.
- Enable aliases for subqueries and joins. Aliases are now automatically prepended to column names from their respective tables.

### Bug Fixes

- Fix query generation in create_view.
- Fix CSV reader with host, port and user credentials. Was previously hard-coded to localhost.
- Fix some corner cases with string and array slicing.
- CHUNK BY was not enabled in sqlparse monkey patch contrib module.

## VULKИ release 19.0.5, 2020-01-22

### Improvements

- System API for managing internal system processors, dictionaries, caches and distributed operations. 
See http://docs.vulkndata.io/system_management/
- NULL type implemented as Literal(Expression('NULL')). Functions such as NULL.is_null() now work as
expected.
- v.drop_columns added for dropping one or more columns. Available as an object management command
and method to a BaseTableDataTable. See http://docs.vulkndata.io/dbmanagement/#vdrop_columnsdatabase-table-42columns.
- DataTables:
    - Add support for ARRAY JOIN / LEFT ARRAY JOIN.
    - Add support for WITH TOTALS to group_by.
    - DataTables now support table/query level aliases in joins and sub-queries.

### Bug Fixes

- Fixed "in_" and similar operators for testing set membership. Now datatable.in_(other_datatable) 
works as expected.
- Python sets/arrays were not correctly parsed handled in the "in_" operator and similar set methods. 
Now datatable.in_([1,2,3]) works as expected.
- group_by / order_by / having / limit / limit_by did not correctly parse Python types into strings
meaning v.select(String(n='col1')).group_by(String(n='col1')) would fail. Behavior is now as expected.
- Float32/Float64 base (Float) inherited from TypeBase instead of Numeric meaning common math operations
failed. Now fixed.

### Backward Incompatible Changes

- PEP8 naming conventions applied to most public functions. Older names still work via aliases but
may be deprecated in the future.
- DataFrames term retired in place of DataTables. No external API issues.

### Build/Testing/Packaging Improvements

- Note added regarding console locale.

## VULKИ release 19.0.4, 2020-01-14

### Bug Fixes

- Fix credential passing for remote ClickHouse instances.

## VULKИ release 19.0.3, 2020-01-13

### Bug Fixes

- Fix installation under Ubuntu via pip.

## VULKИ release 19.0.2, 2020-01-11

### Improvements

- RecordSets now support plain lists and numpy ndarrays
- Allow Vulkn to take Workspace objects and determine the backend automatically
- Numeric types now support lshift and rshift bitwise operations
- Numerous documentation updates:
    - Variables and declarations
    - Operators
    - DataFrames (overview, general reference, extensions, execution, joins, working with results)
    - Extensions (vectorize_by, chunk_by)
    - Workspaces (local, remote, programmatically and via vulkn CLI)
    - Data Loading (CSV only at this stage)

### Bug Fixes

- DataFrame copy_set operations set bool values correctly (fixes .distinct() operation)
- Avoid potential divide by zero error with RandomDataFrames
- Fix string formatting in funcs.not
- Fix confusion with bitwise and logical operators
- Disable compile_expressions in Workspace templates (issue with linking?)

## VULKИ release 19.0.1, 2020-01-01

### Build/Testing/Packaging Improvements

* Added basic PyPy support for installation through pip

## VULKИ release 19.0.0, 2019-12-30

Alpha Proof Of Concept release.

### About

VULKИ (Vulkn, vulcan) is specialised engine and suite of tools for manipulating and managing large volumes of data. ClickHouse, the high-performance Open Source OLAP database, underpins Vulkn and provides the core of the system.

Note: VULKИ 19.0.0 is a Proof Of Concept release. Expect APIs to change in the coming releases as Vulkn reaches stability.

### Initial Features

* Python clients
    - CLI client in 'single' shot mode.
    - Future releases will allow for persistent CLI clients, Python native and HTTP clients.
    - Hybrid client will use any/all of the above depending on specific operation.
* Python DBMS bindings for management
    - Mostly complete DBMS bindings. Allowing for DBMS management including tables, partitions, views and materialized views.
* Python DataFrame interface    
    - DataFrame interface support query strings and ORM/functional/Spark-like interfaces.
    - Functional datatables include Numbers*, Range*, One*, QueryString, SelectQuery, UpdateQuery, DeleteQuery. 
    - JoinDataFrame allows for all join types including ASOF joins.
    - Support for Pandas DataFrames.
* Python datatype bindings
    - Datatype bindings for most ClickHouse types, domains and functions including Vector types that resolve to either columns or arrays.
    - Functions/types can be extended within Python and used within the DataFrame interface.
    - ArrayVector and ColumnVector types can be cached/calculated and stored on ClickHouse as a distributed stack. Vulkn session caching provides references for accelerating computations from these types.
* Reader interface for loading external data
    - Initial release only supports CSV files.
    - ColumnDefs for schema definitions.
    - Support for automated schema creation and type inference. Supports most ClickHouse datatypes including Enums and LowCardinality.
* Folios and Workspaces
    - Workspaces are standalone desktop instances of ClickHouse, coupled with the Python API, targeting data science workloads.
    - Workspaces can be either persistent or temporary.
    - Folios group workspaces by storage/volume allowing for re-usable workspaces/private databases.
    - This release includes only rudimentary/simple support for workspaces.
* SQL Engine
    - Initial SQL engine with AST rewriting interface.
    - Library system for loading custom AST parsers and functions.
* SQL Extensions
    - vector* functions - Perform SQL function rewriting for vector* functions. Supports VECTORIZE BY clause.
    - CHUNK BY - Dynamically generate UNION ALL statements with a modulos WHERE clause based on the chunk key. This statement will most likely be deprecated as the execution mechanisms within ClickHouse address the various non-performant cases.
    - VECTORIZE BY - Specialised time-series focused extension that creates column vectors for the specific metric for each key sorted by the sort_key.
* SQL vector functions
    - Rudimentary SQL:2003 support using VECTORIZE BY (key ..., sort_key).
        - ROW_NUM - vectorRowNumber(column) - for each (key, sort_key) row emit a number starting from 1
        - FIRST - vectorFirst(column) - emit the first row in the (key, sort_key)
        - LAST - vectorLast(column) - emit the last row in the (key, sort_key)
        - LAG - vectorLag(column (, offset=1, default='NULL')) - emit the column value offset rows behind the current row
        - LEAD - vectorLead(column (, offset=1, default='NULL')) - emit the column value offset rows ahead of the current row
        - DENSE_RANK - vectorDenseRank(column) - as per ROW_NUM, calculate the rank of each value relative to the other excluding ties
        - CUME_DIST - vectorCumeDist(column) - calculate the cumulative distance to a maximum of 1 of the first row to the last
        - PERCENT_RANK - vectorPercentRank(column) - as above except use percentages starting from 0
        - NTH_VALUE - vectorNth(column, nth) - return every nth value in the set
        - Misc. standard aggregates (min, max, avg..) using vectorAgg(aggregate_function, column)
    - Others:
        - vectorWindow(column, (, window_backwards=0, window_forwards=0)) - generate sub-vectors of abs(window_forwards)+abs(window_backwards) length (returns a vector of vectors)
        - vectorWindowAgg(aggregate_function, column, window_backwards=0, window_forwards=0) - calculate the aggregate_function on sub-vectors and returns a single value for each sub-vector.
        - vectorCut(column, length) - divide the column vector into vectors of length sub-vectors
        - vectorDelta(column) - delta the current value of column with the previous value
        - vectorAccumulate(column) - maintain a running sum for the specific column
    - Finance:
        - vectorElliotWaveOscillator(column) - Calculate the Elliot Wave Oscillator of the vector
        - vectorDollarValue(price, volume) - Calculate the Dollar Value
* Note the following are unsupported in this release:
    - Table functions other than numbers, one.
    - All input formats other than CSV/CSVWithNames.
    - median aggregation function variants.
    - quantile aggregation function variants.
    - Type conversion of nested types. POC working with Python however is too slow using Pandas.
    - SQL:2003 window functions RANK and NTILE.
    - Tuple and matrix types
    - All interactions with MergeVectors - experimental API/internal POC implementation only

### Improvements

### Bug Fixes

### Backward Incompatible Changes

### Performance Improvements

### Build/Testing/Packaging Improvements
