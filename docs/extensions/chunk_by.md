## *chunkBy(chunkkey: tuple, chunksize: int)*

* Parameters
    * ```chunkkey: tuple``` - the key or composite key to chunk on (using cityHash64)
    * ```chunksize: int``` - size of processing splits, generally no more than the number of CPU cores.
* Returns: ```vulkn.dataframe.SelectQueryDataFrame```
---

```CHUNK BY``` is a Vulkn extension that addresses some performance bottlenecks in ClickHouse in
cases where finalizing a function, generally an aggregation, results in utilization of only a 
single thread. This is only of use when a result or aggregation can be multiplexed by a key.

**Example**

When using histogram function across unique keys we can accelerate the execution by telling 
ClickHouse to split the query into multiple chunks/keys and process these independently.

Either of the following queries:

```python
v.table('timeseries_devices').select('key',funcs.agg.histogram(10, bytes)).groupBy('key').chunkBy('key',2).s
v.q('select key, histogram(10)(bytes) from timeseries_devices group by key chunk by (key, 2)').s
```

Will be converted to the following valid ClickHouse SQL:

```sql
SELECT key, histogram(10)(bytes) FROM timeseries_devices WHERE cityHash64(key)%2 = 0 GROUP BY key
UNION ALL
SELECT key, histogram(10)(bytes) FROM timeseries_devices WHERE cityHash64(key)%2 = 1 GROUP BY key
```

Note that ```CHUNK BY``` will only work in specific cases and will be deprecated once the ClickHouse
core team address any lagging performance issues in this area.