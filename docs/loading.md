Vulkn provides an automated type inference and data loading interface similar to other BigData tools.

The current, Proof Of Concept, release only supports CSV file loads from the local POSIX filesystem.
Exporting is not yet supported. It is also dependant on shell pipelines with ```cat``` and 
```clickhouse-client``` using only a single thread. This will be converted to a multi-processing 
pure python method in future releases.

## Loading CSV files

TODO: Provide more information here.

### Examples

-   Load the CSV file ```elements.csv``` into the table ```default.elements```, overwriting if required. 
    Use a ```MergeTree``` engine with default configuration. Use the CSV header for column names and use type
    inference to determine the column data types.
    ```python
    df = (v
        .read.format('csv')
        .options(header=True,
                overwrite=True,
                infer_schema=True,
                engine=engines.MergeTree())
        .load('file:///home/ironman/elements.csv', database='default', table='elements'))
    ```
    The load operation returns a DataFrame object that can immediately be used for queries.
    ```python
    >>> df.count().s

      row    count()
    -----  ---------
        1        118

    (1 row)
    ```
    Display the table schema. Note how LowCardinality and Nullable modifiers have also been determined.
    ```python
    >>> v.d('elements').s

      row  name                      type                                default_type    default_expression    comment    codec_expression    ttl_expression
    -----  ------------------------  --------------------------------  --------------  --------------------  ---------  ------------------  ----------------
        1  atomic_number             UInt8                                        nan                   nan        nan                 nan               nan
        2  symbol                    LowCardinality(String)                       nan                   nan        nan                 nan               nan
        3  name                      LowCardinality(String)                       nan                   nan        nan                 nan               nan
        4  atomic_mass               LowCardinality(String)                       nan                   nan        nan                 nan               nan
        5  cpk                       LowCardinality(String)                       nan                   nan        nan                 nan               nan
        6  electronic_configuration  LowCardinality(String)                       nan                   nan        nan                 nan               nan
        7  electronegativity         Nullable(Float32)                            nan                   nan        nan                 nan               nan
        8  atomic_radius             LowCardinality(Nullable(String))             nan                   nan        nan                 nan               nan
        9  ion_radius                LowCardinality(Nullable(String))             nan                   nan        nan                 nan               nan
       10  van_der_waals_radius      LowCardinality(Nullable(String))             nan                   nan        nan                 nan               nan
       11  ie_1                      LowCardinality(Nullable(String))             nan                   nan        nan                 nan               nan
       12  ea                        LowCardinality(Nullable(String))             nan                   nan        nan                 nan               nan
       13  standard_state            Nullable(String)                             nan                   nan        nan                 nan               nan
       14  bonding_type              Nullable(String)                             nan                   nan        nan                 nan               nan
       15  melting_point             Nullable(UInt16)                             nan                   nan        nan                 nan               nan
       16  boiling_point             Nullable(UInt16)                             nan                   nan        nan                 nan               nan
       17  density                   LowCardinality(Nullable(String))             nan                   nan        nan                 nan               nan
       18  metal                     String                                       nan                   nan        nan                 nan               nan
       19  year_discovered           LowCardinality(String)                       nan                   nan        nan                 nan               nan
       20  group                     Int8                                         nan                   nan        nan                 nan               nan
       21  period                    UInt8                                        nan                   nan        nan                 nan               nan

    (21 rows)
    ```
-   In this example we enable the column 'snake_case' feature and enable Enum detection.
    ```python
    df = (v
        .read.format('csv')
        .options(header=True,
                overwrite=True,
                infer_schema=True,
                allow_enums=True,
                column_format='snake_case',
                engine=engines.MergeTree())
        .load('file:///home/ironman/nyc.csv', database='default', table='nyc_taxi'))
    ```
    ```
    >>> v.d('nyc_taxi').s

    row  name                type                           default_type    default_expression    comment    codec_expression    ttl_expression
    -----  ------------------  ---------------------------  --------------  --------------------  ---------  ------------------  ----------------
        1  medallion           LowCardinality(String)                  nan                   nan        nan                 nan               nan
        2  hack_license        LowCardinality(String)                  nan                   nan        nan                 nan               nan
        3  vendor_id           Enum8(\'CMT\' = 1)                      nan                   nan        nan                 nan               nan
        4  rate_code           UInt8                                   nan                   nan        nan                 nan               nan
        5  store_and_fwd_flag  Enum8(\'N\' = 1, \'Y\' = 2)             nan                   nan        nan                 nan               nan
        6  pickup_datetime     DateTime                                nan                   nan        nan                 nan               nan
        7  dropoff_datetime    DateTime                                nan                   nan        nan                 nan               nan
        8  passenger_count     UInt8                                   nan                   nan        nan                 nan               nan
        9  trip_time_in_secs   UInt16                                  nan                   nan        nan                 nan               nan
       10  trip_distance       Float32                                 nan                   nan        nan                 nan               nan
       11  pickup_longitude    Float64                                 nan                   nan        nan                 nan               nan
       12  pickup_latitude     Float64                                 nan                   nan        nan                 nan               nan
       13  dropoff_longitude   Float64                                 nan                   nan        nan                 nan               nan
       14  dropoff_latitude    Float64                                 nan                   nan        nan                 nan               nan
       15  tolls_amount        Float32                                 nan                   nan        nan                 nan               nan
       16  tip_amount          Float32                                 nan                   nan        nan                 nan               nan
       17  total_amount        Float32                                 nan                   nan        nan                 nan               nan
       18  mta_tax             Float32                                 nan                   nan        nan                 nan               nan
       19  fare_amount         Float32                                 nan                   nan        nan                 nan               nan
       20  payment_type        Enum8(\'CRD\' = 1)                      nan                   nan        nan                 nan               nan
       21  surcharge           Float32                                 nan                   nan        nan                 nan               nan

    (21 rows)
    ```
-   For this example we use a custom configuration for the MergeTree engine.
    ```python
    df = (v
        .read.format('csv')
        .options(header=True,
                overwrite=True,
                infer_schema=True,
                allow_enums=False,
                column_format='snake_case',
                engine=engines.MergeTree(
                    partition_by=('toDate(parsed_date)',),
                    order_by=('ip_layer_protocol_code','parsed_date','time_seconds',)))
        .load('file:///home/ironman/Downloads/netflow/nf/nf-chunk1.csv', database='default', table='netflow'))
    ```
-   We can also re-use or specify schemas to avoid the inference overhead.
    ```python
    >>> pprint.pprint(v.getSchema('netflow'))
    [ColumnType('time_seconds', 'Float64', default_kind='nan', default_expression='nan' compression_codec='nan'),
    ColumnType('parsed_date', 'DateTime', default_kind='nan', default_expression='nan' compression_codec='nan'),
    ColumnType('date_time_str', 'LowCardinality(String)', default_kind='nan', default_expression='nan' compression_codec='nan'),
    ColumnType('ip_layer_protocol', 'UInt8', default_kind='nan', default_expression='nan' compression_codec='nan'),
    ColumnType('ip_layer_protocol_code', 'String', default_kind='nan', default_expression='nan' compression_codec='nan'),
    ColumnType('first_seen_src_ip', 'LowCardinality(String)', default_kind='nan', default_expression='nan' compression_codec='nan'),
    ColumnType('first_seen_dest_ip', 'LowCardinality(String)', default_kind='nan', default_expression='nan' compression_codec='nan'),
    ColumnType('first_seen_src_port', 'UInt16', default_kind='nan', default_expression='nan' compression_codec='nan'),
    ColumnType('first_seen_dest_port', 'UInt16', default_kind='nan', default_expression='nan' compression_codec='nan'),
    ColumnType('more_fragments', 'UInt8', default_kind='nan', default_expression='nan' compression_codec='nan'),
    ColumnType('cont_fragments', 'UInt8', default_kind='nan', default_expression='nan' compression_codec='nan'),
    ColumnType('duration_seconds', 'UInt16', default_kind='nan', default_expression='nan' compression_codec='nan'),
    ColumnType('first_seen_src_payloadbytes', 'UInt32', default_kind='nan', default_expression='nan' compression_codec='nan'),
    ColumnType('first_seen_dest_payloadbytes', 'UInt32', default_kind='nan', default_expression='nan' compression_codec='nan'),
    ColumnType('first_seen_src_total_bytes', 'UInt32', default_kind='nan', default_expression='nan' compression_codec='nan'),
    ColumnType('first_seen_dest_total_bytes', 'UInt32', default_kind='nan', default_expression='nan' compression_codec='nan'),
    ColumnType('first_seen_src_packet_count', 'UInt16', default_kind='nan', default_expression='nan' compression_codec='nan'),
    ColumnType('first_seen_dest_packet_count', 'UInt16', default_kind='nan', default_expression='nan' compression_codec='nan'),
    ColumnType('record_force_out', 'UInt8', default_kind='nan', default_expression='nan' compression_codec='nan')]
    ```
    ```python
    df = (v
        .read.format('csv')
        .options(header=True,
                overwrite=True,
                schema=schema,
                engine=engines.MergeTree(
                    partition_by=('toDate(parsed_date)',),
                    order_by=('ip_layer_protocol_code','parsed_date','time_seconds',)))
        .load('file:///home/ironman/Downloads/netflow/nf/nf-chunk1.csv', database='default', table='netflow'))
    ```