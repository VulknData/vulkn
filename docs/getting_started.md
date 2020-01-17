# Getting Started

## System Requirements

- Any recent Linux supported by ClickHouse and Python
- Latest ClickHouse server and client binaries (>= 19.15.x). See the [ClickHouse documentation](https://clickhouse.yandex/docs/en/getting_started/#installation) for details on installing ClickHouse.
- Python (>= 3.7.x). We recommend the latest [Anaconda Python distribution](https://www.anaconda.com/distribution/).

## Installation

Vulkn itself is a pure Python application and can be installed using pip.

!!! note
    VULKИ 19.0.0 has only been used / tested within the latest Ubuntu and Mint LTS environments and is unlikely to function as expected under other distributions.

The following has been validated on Ubuntu Xenial and Bionic. Vulkn should work / install on any other system running Python 3.7.x or greater.

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.7 python3.7-dev python3-pip
sudo python3.7 -m pip install vulkn
```

You should also ensure your systems console encoding is set to a valid non-latin/ASCII encoding such as en_US.UTF-8 (or your preferred/local extended character set)

```bash
sudo localectl set-locale LANG=en_US.UTF-8
```

## Using the VULKN CLI

The Vulkn CLI is a simple command line interface that enables interactive exploration and analytics on the Linux console. To follow the example below run ```vulkn --local``` from a terminal.

```text
(base) ironman@hulk ~$ vulkn --local

2019.10.11 10:14:28.709940 [ 1 ] {} <Information> : Starting ClickHouse 19.16.1.1467 with revision 54427
2019.10.11 10:14:28.709992 [ 1 ] {} <Information> Application: starting up
2019.10.11 10:14:28.712126 [ 1 ] {} <Trace> Application: Will mlockall to prevent executable memory from being paged out. It may take a few seconds.
2019.10.11 10:14:28.732955 [ 1 ] {} <Trace> Application: The memory map of clickhouse executable has been mlock'ed
2019.10.11 10:14:28.733106 [ 1 ] {} <Debug> Application: Set max number of file descriptors to 1048576 (was 1024).
2019.10.11 10:14:28.733114 [ 1 ] {} <Debug> Application: Initializing DateLUT.
2019.10.11 10:14:28.733117 [ 1 ] {} <Trace> Application: Initialized DateLUT with time zone 'UTC'.
2019.10.11 10:14:28.734904 [ 1 ] {} <Debug> ConfigReloader: Loading config '/tmp/ironman-8155347b-7857-453b-8af7-7199cf49b25a/etc/users.xml'
2019.10.11 10:14:28.735279 [ 1 ] {} <Information> Application: Loading metadata from /tmp/ironman-8155347b-7857-453b-8af7-7199cf49b25a/clickhouse/
2019.10.11 10:14:28.735797 [ 1 ] {} <Debug> Application: Loaded metadata.
2019.10.11 10:14:28.735812 [ 1 ] {} <Information> BackgroundSchedulePool: Create BackgroundSchedulePool with 16 threads
2019.10.11 10:14:28.737570 [ 1 ] {} <Information> Application: Listening http://[::1]:8124
2019.10.11 10:14:28.737641 [ 1 ] {} <Information> Application: Listening for connections with native protocol (tcp): [::1]:9001
2019.10.11 10:14:28.737690 [ 1 ] {} <Information> Application: Listening http://127.0.0.1:8124
2019.10.11 10:14:28.737723 [ 1 ] {} <Information> Application: Listening for connections with native protocol (tcp): 127.0.0.1:9001
2019.10.11 10:14:28.738090 [ 1 ] {} <Information> Application: Available RAM: 62.60 GiB; physical cores: 8; logical cores: 16.
2019.10.11 10:14:28.738103 [ 1 ] {} <Information> Application: Ready for connections.

Добро пожаловать to VULKИ version 2019.1.1!

██╗   ██╗██╗   ██╗██╗     ██╗  ██╗███╗   ██╗
██║   ██║██║   ██║██║     ██║ ██╔╝████╗  ██║
██║   ██║██║   ██║██║     █████╔╝ ██╔██╗ ██║
╚██╗ ██╔╝██║   ██║██║     ██╔═██╗ ██║╚██╗██║
 ╚████╔╝ ╚██████╔╝███████╗██║  ██╗██║ ╚████║
  ╚═══╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝                    

The developer friendly real-time analytics engine powered by ClickHouse.

VULKИ entrypoint initialized as 'v'.
```

Invoking ```vulkn``` with the ```--local``` option has automatically launched a temporary workspace (ClickHouse backend). See the Workspaces section for more detail on what a Workspace is.

### Your first Vulkn application

Now it's time to have some fun with Vulkn. The following example uses ArrayVectors to create some sample columns. Enter the following into the Vulkn CLI.
```python
num_rows = 25000000

series_key = ArrayVector.range(1,250000).cast(String).map('concat', String('device-')).take(num_rows).cache()
timestamp = ArrayVector.rand(DateTime('2019-01-01 00:00:00'), DateTime('2019-01-01 23:59:59'), num_rows).cast(DateTime).cache()
temperature = ArrayVector.norm(80,10,int(num_rows/2)).cast(Float32).join(ArrayVector.norm(95,5,int(num_rows/2)).cast(Float32)).cache()
bytes = ArrayVector.rand(1, 8192, num_rows).cast(UInt16).cache()
```

### So whats going on here?

First we're creating a list of 250k integers (```UInt64```).

```python
series_key = ArrayVector.range(1,250000)
```

Next we convert the integer types to a ```String``` type.

```python
series_key = ArrayVector.range(1,250000).cast(String)
```

Now we can use the ```concat``` function to prepend the string 'device-' to each value

```python
series_key = ArrayVector.range(1,250000).cast(String).map('concat', String('device-'))
```

We now pull out num_rows (25 million) values from the vector. The ```take()``` function repeats or truncates the vector depending on the required length.

```python
series_key = ArrayVector.range(1,250000).cast(String).map('concat', String('device-')).take(num_rows)
```

Finally we cache the vector. Until this point our ```cast()```, ```map()``` and ```take()``` operations are yet to be executed. This is called lazy evaluation.

```python
series_key = ArrayVector.range(1,250000).cast(String).map('concat', String('device-')).take(num_rows).cache()
```

The timestamp and bytes columns are random values of DateTime and UInt16 types within a range. The temperature column is a bit different and is constructed by joining two separate vectors, each representing a normal distribution (bell) curve with different properties - this approximates morning and afternoon peaks in temperature for a device based on utilisation. 

### From Vectors to Tables

The four equal length vectors can now be combined to form a table. We have to assign names/aliases for both the table and vectors.

```python
data = v.table.fromVector(
    'default.timeseries_devices',
    (series_key.alias('series_key'), timestamp.alias('timestamp'), temperature.alias('temp'), bytes.alias('bytes')),
    engines.Memory(),
    replace=True)
```

The ```fromVector()``` call returns a ```DataTable```. This is a standard relational 'table' (or query) similar to DataTables found within other data projects. Now we can execute aggregations and queries, including joins and subqueries with other DataTables against this object.

```python
>>> data.count().show()

  row    count()
-----  ---------
    1   25000000

(1 row)

>>> data.select('*').limit(10).show()

  row  series_key    timestamp               temp    bytes
-----  ------------  -------------------  -------  -------
    1  device-1      2019-01-01 21:46:09  82.0007     2104
    2  device-2      2019-01-01 09:49:26  74.9356     3662
    3  device-3      2019-01-01 20:36:41  77.5353     7642
    4  device-4      2019-01-01 00:03:46  77.4789     3219
    5  device-5      2019-01-01 09:00:39  72.738      6559
    6  device-6      2019-01-01 18:41:12  83.689      3478
    7  device-7      2019-01-01 07:54:49  68.2859       34
    8  device-8      2019-01-01 16:34:28  88.9767     6903
    9  device-9      2019-01-01 12:45:35  74.6222     2367
   10  device-10     2019-01-01 09:20:28  63.2291     4436

(10 rows)
```

You can also issue standard SQL queries against the table.

```python
>>> v.q("SELECT max(timestamp), avg(temp), median(bytes) FROM default.timeseries_devices").show()

  row  max(timestamp)         avg(temp)    median(bytes)
-----  -------------------  -----------  ---------------
    1  2019-01-01 23:59:59      87.5018             4114

(1 row)
```

## Where to next?

Now that you've created a few vectors, a DataTable and executed some queries it's time to explore other topics such as ASOF joins, SQL extensions and loading data.

