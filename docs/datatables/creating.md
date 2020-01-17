# Creating Tables & Writing Data

Vulkn allows you to create and append to tables as you would any other data system. 

Each DataTable object supports creating new tables and appending to existing tables.

---

## *write(database, table, engine=None, mode=WriteMode.Create)*

* Parameters
    * ```database: str``` - the database to write the table to
    * ```table: str``` - the tablename to write to
    * ```engine: vulkn.engines.*``` - the engine configuration to use for the table (default None)
    * ```mode: vulkn.datatable.WriteMode``` - the strategy to use when writing the data - whether to 
    Create, Append or Replace the table (if it exists).
---

Writes/creates or appends the DataTable to a table with the specified engine.

### Available WriteModes

Valid WriteModes (```vulkn.datatable.WriteMode```) are:

* ```WriteMode.Create``` - Create the table if it doesn't exist
* ```WriteMode.Append``` - Append to the table if it does exist (will result in create otherwise)
* ```WriteMode.Replace``` - Replace the table (overwrite) if it already exists

### Examples

The following two code blocks are effectively identical:

```sql
DROP TABLE IF EXISTS data.agg_events;

CREATE TABLE data.agg_events 
ENGINE = MergeTree ORDER BY (geo_id)
AS
    SELECT
        geo_id,
        uniqExact(event_msg) AS total_uniq_messages,
        sum(event_metric) AS sum_event_metrics
    FROM data.events
    GROUP BY geo_id;

SELECT count() FROM data.agg_events;
```

```python
import vulkn.engines as engines
from vulkn.datatable import WriteMode

df = (v.table('data.events')
    .select('geo_id',
            funcs.agg.uniqExact('event_msg').alias('total_uniq_messages'),
            funcs.agg.sum('event_metric').alias('sum_event_metrics'))
    .groupBy('geo_id')
    .write('data', 'agg_events',
           engine=engines.MergeTree(order_by=('geo_id',)), WriteMode.Replace))

df.count().s
```

Efficiencies, code re-use and maintainability become apparent in more complex examples.

In the next example we first define a table engine strategy/profile. We then define a template query
for a very large table, data.events, that we wish to join/denormalize with a dimension table. Because
the tables are very large, and we can't hold all the data in memory, we iterate through all unique
geo_id dimensions and append the results to the events.denomalized_events table.

The Append WriteMode will Create the table on first call and append to the table on subsequent calls.
If we had more than a handful of geo_ids the SQL-only version becomes unfeasible.

```python
import vulkn.engines as engines
from vulkn.datatable import WriteMode

table_profile = engines.MergeTree(partition_by=('toDate(event_date)',),
                                  order_by=('geo_id','event_date',))

events = v.q('select * from data.events').where("geo_id == {geo_id:UInt32}").alias('e')
dimensions = v.table('default.dims').select('geo_id', 'geo_location', 'geo_coords').alias('d')

for g in v.table('default.dims').select('geo_id').distinct().r:
    df = (events
        .lj(dimensions, ('geo_id',))
        .select('d.*', 'e.*')
        .params({'geo_id': g['geo_id']})
        .write('events', 'denormalized_events', engine=table_profile, WriteMode.Append))

    print(f'events.denormalized_events total count is now {df.count().l[0][0]}')
```
