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
    - Functional dataframes include Numbers*, Range*, One*, QueryString, SelectQuery, UpdateQuery, DeleteQuery. 
    - JoinDataFrame allows for all join types including ASOF joins.
    - Support for Pandas dataframes.
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