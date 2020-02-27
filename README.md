## VULKИ

VULKИ (Vulkn) is a specialized, environmentally friendly, eco-system for manipulating and managing large volumes of data at petabyte scale.

Vulkn is underpinned by the high-performance Open Source OLAP database, Yandex ClickHouse. Rather than re-invent the wheel (or mask the amazing technology that is ClickHouse), Vulkn focuses on the areas of DataOps, simplification and automation. Users can easily extend Vulkn, and the SQL layer, with their own SQL clauses and functions via Python as well as use Python bindings to work with ClickHouse in much the same way they would other modern data systems, specifically those based on functional programming.

### Short-term Roadmap

February/March 2020

- Simple SQL and Vulkn ORM UDF support
- Function cleanup/introspection
- Support all types/functions for current stable/testing
- Support for user/group/quota/workload management (in ClickHouse core)
- ~~HTTP interface (rather than fork/exec client)~~ (done)
- Proof Of Concept phase ends
- Initial implementation of Vulkn server

### Documentation

Documentation is available at http://docs.vulkndata.io. Note this is currently incomplete and content will be updated/provided over the coming weeks.

### Initial Release

The initial release (19.0.0) is a Proof Of Concept. Expect APIs to change in the coming releases as Vulkn reaches stability. The following features are available:

- SQL rewriting engine with library support
- Workspaces (very proof of concept)
- Python data type bindings
- Vector types - ArrayVector, ColumnVector, MergeVector
- SQL extensions - CHUNK BY, VECTORIZE BY
- SQL vector functions (basic SQL:2003 Window Functions)

### Installation

Vulkn has only been tested with recent versions of Ubuntu and Python 3.7. You will need to have a
working Python 3.7.x environment with pip.

Ensure you have installed ClickHouse (both server and client):

```bash
sudo apt install clickhouse-server clickhouse-client clickhouse-common
```

You should also ensure your systems console encoding is set to a valid non-latin/ASCII encoding such as en_US.UTF-8 (or your preferred/local extended character set)

```bash
sudo localectl set-locale LANG=en_US.UTF-8
```

#### Installation with pip

1. Install Vulkn via pip.

    ```bash
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install -y python3.7 python3.7-dev python3-pip
    sudo python3.7 -m pip install vulkn
    ```

#### Installation from source (for developers)

1. Install Vulkn via ```git clone```.

    ```bash
    git clone https://github.com/VulknData/vulkn.git
    cd vulkn
    ```

2. Install required packages. Note that it may make sense to do this within a virtual environment.

    ```bash
    pip install -r requirements.txt
    ```

3. You can start the Vulkn CLI using the following. This creates a temporary Vulkn Workspace.

    ```bash
    cd scripts
    source env.sh
    ./v --local

    # Or use ./v to connect to your running local ClickHouse instance
    ```

### Getting Started

Let's try out the Python API with a 25 million row time-series table. In this example we'll create a table from a group of ArrayVectors with 10,000 unique series, a random DateTime dimension over the course of a day and two metrics (temperature, bytes). For the metrics we'll simulate a double peak day by generating concatenated normal distribution curves. These operations should execute in several seconds on any modern computer with 4-8GB of RAM.

If you installed Vulkn via pip use ```vulkn --local``` to start a local session (or follow Step 3. from the source installation option above).

Note that if you are connecting to a remote (or local ClickHouse instance not managed by Vulkn) you may need to manually create the "vulkn" database and ensure the connecting user can create tables under this database.

```bash
ironman@hulk ~/ $ vulkn --local

2020.01.01 11:52:14.072561 [ 1 ] {} <Trace> Pipe: Pipe capacity is 1.00 MiB
2020.01.01 11:52:14.072619 [ 1 ] {} <Information> : Starting ClickHouse 19.19.1.2024 with revision 54430
2020.01.01 11:52:14.072651 [ 1 ] {} <Information> Application: starting up
2020.01.01 11:52:14.078485 [ 1 ] {} <Trace> Application: Will mlockall to prevent executable memory from being paged out. It may take a few seconds.
2020.01.01 11:52:14.103994 [ 1 ] {} <Trace> Application: The memory map of clickhouse executable has been mlock'ed
2020.01.01 11:52:14.104171 [ 1 ] {} <Debug> Application: Set max number of file descriptors to 1048576 (was 1024).
2020.01.01 11:52:14.104180 [ 1 ] {} <Debug> Application: Initializing DateLUT.
2020.01.01 11:52:14.104182 [ 1 ] {} <Trace> Application: Initialized DateLUT with time zone 'UTC'.
2020.01.01 11:52:14.105815 [ 1 ] {} <Debug> ConfigReloader: Loading config '/tmp/jason-1f1b3dd6-703c-40d8-9573-f0f07fcda44a/etc/users.xml'
2020.01.01 11:52:14.106233 [ 1 ] {} <Information> Application: Loading metadata from /tmp/jason-1f1b3dd6-703c-40d8-9573-f0f07fcda44a/clickhouse/
2020.01.01 11:52:14.106817 [ 1 ] {} <Information> DatabaseOrdinary (default): Total 0 tables and 0 dictionaries.
2020.01.01 11:52:14.106827 [ 1 ] {} <Information> DatabaseOrdinary (default): Starting up tables.
2020.01.01 11:52:14.106876 [ 1 ] {} <Debug> Application: Loaded metadata.
2020.01.01 11:52:14.106887 [ 1 ] {} <Information> BackgroundSchedulePool: Create BackgroundSchedulePool with 16 threads
2020.01.01 11:52:14.109096 [ 1 ] {} <Information> Application: Listening for http://[::1]:8124
2020.01.01 11:52:14.109151 [ 1 ] {} <Information> Application: Listening for connections with native protocol (tcp): [::1]:9001
2020.01.01 11:52:14.109202 [ 1 ] {} <Information> Application: Listening for http://127.0.0.1:8124
2020.01.01 11:52:14.109235 [ 1 ] {} <Information> Application: Listening for connections with native protocol (tcp): 127.0.0.1:9001
2020.01.01 11:52:14.109584 [ 1 ] {} <Information> Application: Available RAM: 62.60 GiB; physical cores: 8; logical cores: 16.
2020.01.01 11:52:14.109597 [ 1 ] {} <Information> Application: Ready for connections.

Добро пожаловать to VULKИ version 19.0.1!

██╗   ██╗██╗   ██╗██╗     ██╗  ██╗███╗   ██╗
██║   ██║██║   ██║██║     ██║ ██╔╝████╗  ██║
██║   ██║██║   ██║██║     █████╔╝ ██╔██╗ ██║
╚██╗ ██╔╝██║   ██║██║     ██╔═██╗ ██║╚██╗██║
 ╚████╔╝ ╚██████╔╝███████╗██║  ██╗██║ ╚████║
  ╚═══╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝                    

The developer friendly real-time analytics engine powered by ClickHouse.

VULKИ entrypoint initialized as 'v'.

>>> 
```

```python
# Create four ArrayVectors simulating a time-series

series_key = (ArrayVector
    .range(1,10000).cast('String').map('concat', String('device-')).take(25000000)
    .cache().alias('series_key'))
timestamp = (ArrayVector
    .rand(DateTime('2019-01-01 00:00:00'), DateTime('2019-01-01 23:59:59'), 25000000)
    .cache().alias('timestamp'))
temperature = (ArrayVector.norm(80,10,12500000).join(ArrayVector.norm(95,5,12500000))
    .cache().alias('temperature'))
bytes = ArrayVector.rand(1, 8192, 25000000).cache().alias('bytes')

# Combine the ArrayVectors to create a table, returning a DataTable

data = v.table.fromVector('default.mydata', 
    (series_key, timestamp, temperature, bytes), engines.Memory(), replace=True)

data.count().show()

# Use SQL to aggregations and other queries

v.q("""
    SELECT
        series_key,
        max(timestamp),
        avg(temperature),
        min(bytes)
    FROM default.mydata
    GROUP BY series_key""").show()

# Use Vulkn time-series SQL extensions - calculate the moving average using the current row and two behind/ahead (5 value window)

v.q("""
    SELECT
        series_key, 
        timestamp, 
        bytes,
        vectorWindowAgg(avg, bytes, -2, 2) AS moving_avg 
    FROM default.mydata
    WHERE series_key = 'device-1'
    VECTORIZE BY (series_key, timestamp)""").limit(20).show()

# You can also use the DataTable interface to build up complex queries

v.table('default.mydata').select(funcs.agg.max(col('bytes')).alias('max_bytes')).s

# Results can be returned as a 'pretty print' table (.s, .show()), list of dictionaries (a record) (.r, .to_records()) or a Pandas DataFrame (.p, .to_pandas())

v.table('default.mydata').all().limit(4).r

[
    {'series_key': 'device-1', 'timestamp': '2019-01-01 08:42:29', 'temperature': 94.10629119151686, 'bytes': 6206},
    {'series_key': 'device-2', 'timestamp': '2019-01-01 08:32:24', 'temperature': 75.25278421080404, 'bytes': 5070},
    {'series_key': 'device-3', 'timestamp': '2019-01-01 09:47:07', 'temperature': 83.09766288572209, 'bytes': 3617},
    {'series_key': 'device-4', 'timestamp': '2019-01-01 17:37:49', 'temperature': 77.4298465579733, 'bytes': 3283}
]

# Data sets are also discoverable via the 'data' dictionary

[t for t in v.data.keys() if t == 'default.mydata']
mydata = v.data['default.mydata']
mydata

# <vulkn.datatable.BaseTableDataTable object at 0x7f587af97908>

# Inspect the DataTable properties

mydata.desc().s

row  name         type        default_type    default_expression    comment    codec_expression    ttl_expression
-----  -----------  --------  --------------  --------------------  ---------  ------------------  ----------------
    1  series_key   String               nan                   nan        nan                 nan               nan
    2  timestamp    DateTime             nan                   nan        nan                 nan               nan
    3  temperature  Float64              nan                   nan        nan                 nan               nan
    4  bytes        UInt64               nan                   nan        nan                 nan               nan

(4 rows)

# Create Pandas DataFrames from a Vulkn query

mydata.all().limit(10).p

series_key            timestamp  temperature  bytes
0   device-1  2019-01-01 19:47:24    92.573274   7759
1   device-2  2019-01-01 10:10:34    97.795875   6372
2   device-3  2019-01-01 12:43:20    92.769747   7692
3   device-4  2019-01-01 22:57:42    98.037090   5498
4   device-5  2019-01-01 04:47:13    86.352442   3664
5   device-6  2019-01-01 09:09:17    86.679861   4997
6   device-7  2019-01-01 12:01:05    99.481727   6189
7   device-8  2019-01-01 17:03:07    90.488295   4991
8   device-9  2019-01-01 05:28:43    92.532215    653
9  device-10  2019-01-01 10:47:38    98.021234    192

mydata.all().limit(10).p.dtypes
series_key      object
timestamp       object
temperature    float64
bytes            int64
dtype: object
```

Let's explore the python API.

```python
# Native Vulkn functions/ClickHouse SQL in the Python API

print((UInt8(8).alias('v') != 3).alias('k').cast('String').startswith('a').intDiv(3))

# Using and re-using aliases and variables

s = String('abc,foo').split(',')
col1 = s[1].alias('col1')
clone_col1 = String(name='a')

# Tying it all together with lambdas

func = funcs.arrayMap(lambda x=String(n='x'), y=String(n='y'): x.length() > 3, s, col1, clone_col1)

# Preview the rendered function.

print(func)

# arrayMap((x, y) -> greater(length("x"),3), splitByString(',','abc,foo'), arrayElement(splitByString(',','abc,foo'),1) AS `col1`, "a")

# You can also create libraries of re-usable functions using the Python API.
# Note - Native Python functions and the ability to register functions with the SQL engine are coming in a future release.

def extract_key(column, alias):
    key_id = String(n=column).lower().split('-')[2]
    key = key_id.cast('UInt64').alias(alias)
    return key

def apply_cutoff(arg1, arg2, arg3):
    return funcs.if_(col(arg1) > arg2, arg3, arg2)

# Python datatables

df = (v
    .table('default.mydata')
    .select(
        extract_key('series_key', 'key'),
        apply_cutoff('bytes', 100, 100).alias('newcolumn')
    ).orderBy('key'))

df.show_sql()

"SELECT cast(splitByString('-', lower(series_key))[2], 'UInt64') AS key, if(bytes > 100, 100, 100) AS newcolumn FROM default.mydata ORDER BY key ASC;"

# Load external data

external_data = (v
    .read.format('csv')
    .options(header=True,
            overwrite=True,
            infer_schema=True,
            engine=engines.MergeTree())
    .load('file:///data/my-example-data.csv', database='default', table='example'))

external_data.count().show()
```

### Limitations

The following limitations apply to the 19.0.0 Proof Of Concept release and will be addressed in future versions:

- Security, authentication and authorization is currently not available. We will be implementing LDAP authentication and fine-grained access control.
- All operations are synchronous and single-threaded however operations on the underlying ClickHouse datastore will utilise multiple cores if available. Future versions will be asynchronous.
- Single node. Session management is focussed on a single node only at this stage. You can use Vulkn with a multi-node ClickHouse cluster however sessions and tables will be limited to the originating/master node only. Future versions will be completely distributed allowing for grid computing.
- Sub-selects are required for certain operations with SQL extensions.
- Stream processing is not supported. Vulkn will look to leverage ClickHouse's impressive ingestion performance and real-time reporting rather than provide a dedicated streaming solution.
- Most operations are not constrained by memory. In the future Vulkn will offer more options to serialize to disk.
- Vector matrices are not yet supported however standard table functions are fine.
- Data shuffling is currently offloaded to ClickHouse. There are known performance issues with data shuffle operations and distributed joins within ClickHouse that will be addressed by the core team soon.
- Did we mention this is a POC? Things are brittle and will break. The code is very ugly in places and we intend on major refactoring under the hood ASAP.

### Overview

* SQL Engine
    
    DataOps meets SQL. The SQL engine intercepts and rewrites SQL statements, facilitating clever data orchestration and extension with only a handful of lines of code. The initial SQL engine is very simple at this stage. This release includes a simple library interface for registering SQL extensions and vector functions to support the ```VECTORIZE BY``` extension.

* Workspaces

    A workspace consists of a stand-alone, local instance of the ClickHouse server. When a workspace is instantiated a local instance of ClickHouse is started under the current user. This is coupled to the Python API, along with either temporary or permanent storage. Users can nominate for either temporary or permanent workspaces and manage their workspaces via the vulkn CLI. Permanent workspaces can be thought of as private ClickHouse databases, complete with SQL interfaces, persistent data and managed configuration. Multiple users can launch multiple workspaces on a single machine if desired.

    Workspaces will be extended in the future to offer both local and remote storage with the ability to pull in datasets from remote databases, object stores and filesystems for analysis within the local instance. Given the performance profile of ClickHouse this could offset Cloud costs - organisations will find it faster, cheaper and greener to switch off Hadoop/Spark clusters and simply run offline analytics on a single laptop that pull from a main store when required.

* Python Bindings

    Python bindings for most functions and objects are available as well as a simple DataTable interface.

    * Data Types

        The available data types are:

        * String
        * Date
        * DateTime
        * Float32, Float64
        * Int8, Int16, Int32, Int64
        * UInt8, UInt16, UInt32, UInt64
        * Array

        Functional styles/notation is preferred and types behave like Python types in most cases:

        ```python
        >>> mystr = String('a quick brown box').split(' ').length()[2]
        >>> print(mystr)
        length(splitByString(' ','a quick brown box'))
        >>> one_element = String('a quick brown box').split(' ')[2]
        >>> print(one_element)
        arraySlice(splitByString(' ','a quick brown box'),2,1)
        ```

        Array slices are also supported:

        ```python
        >>> mystr_with_commas = String('a quick brown box').split(' ')[1:3].join(',')
        >>> print(mystr_with_commas)
        arrayStringConcat(',',arraySlice(splitByString(' ','a quick brown box'),1,3))
        >>> v.select(mystr_with_commas).s

          row  arrayStringConcat(arraySlice(splitByString(\' \', \'a quick brown box\'), 1, 3), \',\')
        -----  ----------------------------------------------------------------------------------------
            1  a,quick,brown

        (1 row)
        ```

        You can also mix and match Python types with Vulkn types:

        ```python
        >>> mystr = String('a quick brown box').split(' ').length() > 3
        >>> print(mystr)
        greater(length(splitByString(' ','a quick brown box')),3)
        ```

        Type information is propagated through the function interfaces so String.length() returns a UInt type.

        Note that the function interface will be redesigned in future releases however functionality / APIs will remain mostly unchanged.

    * DataTable interface

        DataTables mimic similar concepts found within Pandas, Apache Spark, Apache Flink and other such systems. They provide an object/functional interface to authoring re-usable transformations and code.

        Mixing DataTables with sub-selects, JOINS and raw SQL (```v.q()```) are all supported.

        Example:

        ```python
        v = Vulkn()

        df = (v
            .table('metrics')
            .select('column', 'another column', String(n='myid'))
            .where('column > 3')
            .orderBy('another column'))

        df2 = df.select('count()')
        ```

        Results can be returned as Pandas DataFrames, dictionaries, JSON or CSV. Basic type mappings with Python/Pandas is supported however nested and array types are returned as objects.
        
        Support for nested and array types for Python and Pandas outputs will be available in a future release as will transparent external data joins / loading with Python objects and Pandas DataFrames.

* Specialized Vector types

    Vulkn provides two vector types - ArrayVector and ColumnVector. ArrayVector types offer moderate performance and are suitable for up to 100 million elements. ColumnVectors can be unlimited (within reason) although some operations will be limited by available memory. ArrayVectors can be converted to ColumnVectors and vice-versa.

    Vectors are useful for generating sample datasets or incremental vector calculations from a large table. Both types support most of the same operations and are interchangeable.

    Note that vector types are not intended/available for Vulkn queries and supplement existing relational processing. The Array type and general purpose data type functions can be used to manipulate tables.

    Vector creation methods:

    * ```range(start, end)``` - generate a vector of Integers/UIntegers starting at start and ending at end.
    * ```rand(start, end, length)``` - generate a random vector of Integers/UIntegers with values between $start and $end of length $length.
    * ```norm(mean, stddev, count)``` - generate a vector of random distribution (bell curve) of count elements with centered around mean of width stddev.
    * ```table(Vulkn table/query)``` - create a vector from a Vulkn table or query result.
    * ```toColumnVector``` - creates a ColumnVector object from an ArrayVector.
    * ```toArrayVector``` - creates an ArrayVector object from a ColumnVector.

    Operations:

    * ```sort``` - sorts the vector by key
    * ```reverse/sort_reverse``` - sort the vector by key descending
    * ```shuffle``` - randomly sort the vector
    * ```cast(type)``` - cast the vector to the specified type
    * ```cut(length)``` - divide the vector in rows of equal elements
    * ```take``` - either reduce or extend the vector by the specified limit. Note that in some cases limit is more efficient than take for reducing the size of a vector.
    * ```limit(limit)``` - reduce the length of the vector by the specified limit 
    * ```flatten``` - flatten a vector containing arrays
    * ```prev``` - shift the entire vector backward one element
    * ```next``` - shift the entire vector forward one element
    * ```delta``` - delta the vector with the preceding value
    * ```join(other_vector)``` - join/concatenate two vectors
    * ```move``` - shift the vector positions elements left or right
    * ```wavg``` - calculate the weighted average of one vector by another
    * ```map``` - apply a function to all elements in the vector
    * ```maplag``` - apply a function pairwise in a lagging fashion - f(current, previous)
    * ```maplead``` - apply a function pairwise in a leading fashion - f(current, next)

    Table creation methods

    * ```v.table.fromVector(name, (vectors,), storage.Type)```

    Multiple vectors can be formed into a standard table called name using engines - ```engines.<Type>```

* Engine Types

    * ```engines.Memory(settings)```
    * ```engines.Log(settings)```
    * ```engines.StripeLog(settings)```
    * ```engines.TinyLog(settings)```
    * ```engines.MergeTree(partitionBy, PrimaryKey, OrderBy, settings)```

* SQL Extensions
    - CHUNK BY

        * Status: alpha
        * Example:
    
            ```sql
            SELECT <cols> FROM table CHUNK BY (key, 2)
            ```

        * Notes: N/A
        
        ```CHUNK BY``` dynamically generates ```UNION ALL``` statements with a modulos ```WHERE``` clause based on the chunk key. This is a simple and effective work around for corner cases where ClickHouse is unable to utilise all CPU cores in some queries.
        
        In the example above the statement will be rewritten to:

        ```sql
        SELECT * FROM (
            SELECT <cols> FROM table WHERE cityHash64(key)%2=0
            UNION ALL
            SELECT <cols> FROM table WHERE cityHash64(key)%2=1
        )
        ```

        This statement will most likely be deprecated as the execution mechanisms within ClickHouse address the various non-performant cases.

    - VECTORIZE BY

        * Status: alpha
        * Example:

            ```sql
            SELECT
                key, sort_key, other_col1, other_col2, metric1, metric2,
                vectorFunction(metric1) AS vector_metric1
                vectorFunction(metric2) AS vector_metric2
            FROM table
            VECTORIZE BY (key, other_col1, other_col2...other_coln, sort_key)
            ```

        * Notes: ```GROUP BY```, ```LIMIT BY```, ```LIMIT```, ```ORDER BY``` and ```SETTINGS``` are not supported in ```VECTORIZE BY``` statements (use sub-selects if required)

        ```VECTORIZE BY``` is a specialized time-series focused extension that creates column vectors for the specific metric for each key sorted by the sort_key (usually time). Additional columns that are not part of the key, sort_key or metrics must be specified in the ```VECTORIZE BY``` clause (other_col..). Vector columns are automatically determined using the leading double-underscore syntax. Non-vector columns will most likely fail to evaluate correctly in vector* functions within a ```VECTORIZE BY``` statement. This syntax may change in the future as the API matures.

        When using ```VECTORIZE BY``` each row has visibility across the entire set of rows for that given key allowing the user to calculate complex metrics that are dependant on part of or the entire dataset for that key. Most SQL:2003 window functions have been implemented using this mechanism in addition to specialized time-series functions.

        For example - to compare the lagging delta of a value of a particular metric against the average for that series you can use the following. Note how the ```vectorAgg(avg)``` function calculates an average value that can be compared across rows and against other vector function derived values. Moving averages / sliding windows are also supported using the ```vectorWindowAgg``` function.

        ```sql
        SELECT 
            id, time, volume, avg_volume, abs(delta_volume) AS delta_volume,
            abs(round(abs(delta_volume) / avg_volume, 2)) AS avg_distance
        FROM (
            SELECT 
                id, time, volume, 
                vectorAgg(avg, __volume) AS avg_volume,
                vectorDelta(__volume) AS delta_volume
            FROM stocks 
            VECTORIZE BY (id, time))

        id                       time   volume   avg_volume   delta_volume   avg_distance

        522243    2019-01-01 10:02:34     2198       1926.9              0              0
        522243    2019-01-01 10:11:55      706       1926.9           1492           0.77
        522243    2019-01-01 10:27:49     3423       1926.9           2717           1.41
        522243    2019-01-01 10:40:32     1374       1926.9           2049           1.06
        522243    2019-01-01 10:42:18     1742       1926.9            368           0.19
        522243    2019-01-01 11:17:46     3916       1926.9           2174           1.13
        522243    2019-01-01 11:27:46     1477       1926.9           2439           1.27
        522243    2019-01-01 11:33:18     1239       1926.9            238           0.12
        522243    2019-01-01 12:17:59     2864       1926.9           1625           0.84
        522243    2019-01-01 12:32:54      330       1926.9           2534           1.32
        4109129   2019-01-01 10:24:32     3850       2323.7           3520           1.51
        4109129   2019-01-01 10:50:35     1332       2323.7           2518           1.08
        4109129   2019-01-01 11:00:59     2897       2323.7           1565           0.67
        4109129   2019-01-01 11:16:26       16       2323.7           2881           1.24
        4109129   2019-01-01 11:18:55      873       2323.7            857           0.37
        4109129   2019-01-01 11:21:58     3553       2323.7           2680           1.15
        4109129   2019-01-01 11:34:44     1699       2323.7           1854            0.8
        4109129   2019-01-01 11:55:22     3227       2323.7           1528           0.66
        4109129   2019-01-01 12:02:35     2349       2323.7            878           0.38
        4109129   2019-01-01 12:14:13     3441       2323.7           1092           0.47

        20 rows in set. Elapsed: 1.298 sec. Processed 50.00 million rows, 1.39 GB (38.52 million rows/s., 1.07 GB/s.)
        ```

        Under the hood ```VECTORIZE BY``` converts values to arrays grouped by the key and non-key columns, sorted by the sort_key. Vector operations are then executed on the underlying arrays. Because these operations can touch the entire keys dataset per row the performance of ```VECTORIZE BY``` may seem very different to a non-```VECTORIZE-BY``` query. At face value, Non-```VECTORIZE-BY``` queries may be able to scan 1 billion cells/s for a given column, whereas a similar ```VECTORIZE``` query will only scan 40 million rows/s. In reality the ```VECTORIZE BY``` query may actually touch the equivalent of 500 million cells/s however the complexity of the operations involved hide this fact.

        As a footnote statements generated by ```VECTORIZE BY``` result in very complex ARRAY JOIN statements. Fortunately these statements can be persisted as views within ClickHouse.

        This statement will most likely be deprecated when window functions are available within ClickHouse core.

        Future versions of Vulkn will include a server component that will expose all extensions and custom functions through a normal ClickHouse ODBC endpoint.

* SQL vector functions

    The following standard vector functions are part of the core library.
    
    As vector functions return vectors (even scalar average functions return vectors) you can chain functions together to calculate complex derivatives and other metrics. For instance, assuming a 15minute timeseries counter, the following calculates the max temperature across a rolling hour every 15mins and then calculates the average of the max for the rolling hour. We've also calculated cumulative sum of the rolling average (2 periods behind, 2 ahead) of the delta of the temperature. 
    
    ```sql
    SELECT
        device,
        location,
        timestamp,
        temperature,
        vectorWindowAgg(max, temperature, -3) AS max_rolling,
        vectorAgg(avg, vectorWindowAgg(max, temperature, -3)) AS avg_max_rolling,
        vectorAccumulate(vectorWindowAgg(avg, vectorDelta(temperature), -2, 2)) AS delta_temp_window_avg_accumulate
    FROM device_series
    WHERE device = 'mydevice-123' AND timestamp BETWEEN '2019-01-01' AND '2019-02-01'
    VECTORIZE BY (device, location, timestamp)
    ```

    Note that the formula for the column max_rolling must be repeated within the nested vectorAgg function. This is due to limitations with the current Vulkn parser. Fortunately, whilst it may seem that we're 'recalculating' the max_rolling value, the underlying ClickHouse engine tracks the relational algebra and ensures the formula is only calculated once.

    #### Supported Vector functions

    - Rudimentary SQL:2003 support using ```VECTORIZE BY (key ..., sort_key)```.
        - ```ROW_NUM - vectorRowNumber(vector_column)``` - for each (key, sort_key) row emit a number starting from 1
        - ```FIRST - vectorFirst(vector_column)``` - emit the first row in the (key, sort_key)
        - ```LAST - vectorLast(vector_column)``` - emit the last row in the (key, sort_key)
        - ```LAG - vectorLag(vector_column (, offset=1, default='NULL'))``` - emit the column value offset rows behind the current row
        - ```LEAD - vectorLead(vector_column (, offset=1, default='NULL'))``` - emit the column value offset rows ahead of the current row
        - ```DENSE_RANK - vectorDenseRank(vector_column)``` - as per ROW_NUM, calculate the rank of each value relative to the other excluding ties
        - ```CUME_DIST - vectorCumeDist(vector_column)``` - calculate the cumulative distance to a maximum of 1 of the first row to the last
        - ```PERCENT_RANK - vectorPercentRank(vector_column)``` - as above except use percentages starting from 0
        - ```NTH_VALUE - vectorNth(vector_column, nth)``` - return every nth value in the set
        - Misc. standard aggregates (min, max, avg..) using ```vectorAgg(aggregate_function, vector_column)```
    - Others:
        - ```vectorWindow(vector_column, (, window_backwards=0, window_forwards=0))``` - generate sub-vectors of abs(window_forwards)+abs(window_backwards) length (returns a vector of vectors)
        - ```vectorWindowAgg(aggregate_function, vector_column, window_backwards=0, window_forwards=0)``` - calculate the aggregate_function on sub-vectors and returns a single value for each sub-vector.
        - ```vectorCut(vector_column, length)``` - divide the column vector into vectors of length sub-vectors
        - ```vectorDelta(vector_column)``` - delta the current value of column with the previous value
        - ```vectorAccumulate(vector_column)``` - maintain a running sum for the specific column
    - Finance:
        - ```vectorElliotWaveOscillator(vector_column)``` - Calculate the Elliot Wave Oscillator of the vector
        - ```vectorDollarValue(price_vector, volume_vector)``` - Calculate the Dollar Value

## FAQ

### Isn't this just an ORM?

No. The SQL / object interface is only one minor / enabling feature. By having a tightly integrated SQL / object / type interface that is free from the usual constraints of an ORM we can implement mechanisms that blur the lines between ORMs, BigData frameworks (like Spark), time-series systems, APL systems, DBMS management utilities, API generation, ML, AI and DataOps orchestration/automation. Vulkn also enables DataOps extensions, that leverage many of the ideas found within DevOps, to allow users to shape the query language itself. The POC release only targets SELECT statements where the AST can be transformed into single statement however we will be extending this to encompass a wider range of possibilities.

### Does Vulkn compete with Hadoop, Spark, Flink?

Spark, Hadoop etc.. have a large, mature and established eco-system with a specific trajectory and path. ClickHouse is capable of ingesting and querying massive volumes of data in real-time (at velocities that exceed the aforementioned systems) however it has a very rigid API that does not allow for custom code without re-compiling the framework (unlike Spark or Hadoop). Custom code has advantages with performance being the limitation. If, at some point, users see benefit in Vulkn or ClickHouse over other tools, we suspect it will be to compliment their respective strengths.

### Is Vulkn a time-series database?

Not specifically although ClickHouse is capable of besting the fastest Open Source and commercial time-series databases in most cases and can match them on a $-for-$ basis for compute. ClickHouse supports in-memory dictionaries/symbol tables, key/value, both in-memory and disk backed tables with memory buffers, distributed execution and ingestion, federated queries, some window/vector operations (more with Vulkn), streaming materialized views and ASOF-joins.

### Does Vulkn support native Python functions?

We have been able to validate 1 million rows/s per core (Core i7) for trivial/untuned Python serialization of a 5 column width table of various data types. 1 million rows/s per core is most likely acceptable for those cases where serialization out to Python is a hard requirement although such throughput is generally too slow for any real work. Preferably users should use the Python API to author Vulkn native functions which support billions of rows/s per core.

ClickHouse -> Python serialization has been validated by others (within the clickhouse-driver project) at over 25-50 million elements per second per core depending on data type/width. We anticipate using this library over our rudimentary tests in the future. 

Once we have the serialization performance nailed down we will be adding support for distributed Pandas/Dask, and by extension, pure-Python functions.

### Do you support AI and ML interfaces

Rudimentary ML is supported within ClickHouse via basic regression and classification methods and CatBoost integration with GPU support. Rather than create an eco-system of ML and AI within ClickHouse, Vulkn will focus on DataOps orchestration of ML and AI coupled with ClickHouse.

### Apache Spark .. or other project .. benchmark is much faster than Vulkn or ClickHouse - what gives?

There are plenty of instances where other technologies will outperform ClickHouse and, coupled with their respective feature set, these may be better solutions for your specific problem. That said, beware of 'snake oil' benchmarks that focus on pre-computed or indexed fields, min/max counts or datasets that are prepared and presented in-memory only. Considering the whole of a problem, from ingestion, through analysis and to ensuring data consistency at rest, ClickHouse, coupled with Vulkn, should prove to be compelling.

### Will you provide other language bindings?

Most likely no, however existing ClickHouse drivers and ORMs in other languages should work with Vulkn SQL without a problem.

### When will the road-map be published?

Soon.

### I like where this is going and I want feature X!

Great! Create a feature request on GitHub and we'll review.

### Can I contribute?

Absolutely! Please see [CONTRIBUTING](CONTRIBUTING.md) for more info.

### Do you provide commercial/Enterprise support?

Not at this stage. Feel free to ping us @ admin@vulkndata.io.

### Can I use Vulkn in my non-GPL FLOSS or commercial project?

Yes! You can use most popular OSI approved licenses for your project. We have used the GPL exclusion mechanism to specifically allow aggregate works providing the aggregate work is released under one of the listed OSI approved licenses and Vulkn itself remains unmodified.

The allowable OSI licenses are:

* Apache License 2.0 (Apache-2.0)
* 3-clause BSD license (BSD-3-Clause)
* 2-clause BSD license (BSD-2-Clause)
* GNU General Public License (GPL)
* GNU Lesser General Public License (LGPL)
* MIT license (MIT)
* Mozilla Public License 2.0 (MPL-2.0)
* Common Development and Distribution License 1.0 (CDDL-1.0)
* Eclipse Public License 2.0 (EPL-2.0)

The GPLv3 enables you to use Vulkn internally within your organization or as part of a web service with no requirement to share your application code or licence it under the GPLv3.

If you modify Vulkn you will have to either contribute your changes or adhere to the requirements of the GPLv3.

If you are wanting to package and distribute the covered (unmodified) work as part of a larger work under a commercial license thats fine too providing you comply using interfaces compatible with the GPL ("at arms length" - pipes, sockets and command-line arguments) or seek an exception from the Licensor.

If you want to modify the work, include it in a proprietary aggregate/license and distribute it, you will need to reach out to us. It is not our intention to expose part of or your entire proprietary/commercial application to an OSI licence. We merely want to protect our efforts thus far as it applies to reciprocal adaptions, modification and minimal appropriate investment to enable sustainable development of the software by the authors.
