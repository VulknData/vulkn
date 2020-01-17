# System Management

The following system functions can be used to manage internal system processors, dictionaries, caches and
distributed operations.

ClickHouse reference - https://clickhouse.yandex/docs/en/query_language/system/

---

## *v.sys.reload_dicts()*

Reload all currently LOADED dictionaries.

---

## *v.sys.reload_dict(dictionary)*

Reload or load a specific dictionary.

* Parameters
    * ```dictionary``` - the name of the dictionary to reload

---

## *v.sys.drop_dns_cache()*

Reset ClickHouse's internal DNS cache.

---

## *v.sys.drop_mark_cache()*

Reset the mark cache (useful for performance testing).

---

## *v.sys.flush_logs()*

Flush logs to the system tables.

---

## *v.sys.reload_config()*

Reload the ClickHouse configuration.

---

## *v.sys.shutdown()*

Shuts down the database instance. Note this will terminate your Vulkn instance.

---

## *v.sys.kill()*

Force kill the database instance (and your Vulkn session).

---

## *v.sys.stop_dist_sends(database, table)*

Disable background data distribution for the specified table.

* Parameters
    * ```database``` - the database containing the table to operate on
    * ```table``` - the table to operate on

---

## *v.sys.flush_dist(database, table)*

Flush all data to the cluster nodes synchronously.

* Parameters
    * ```database``` - the database containing the table to operate on
    * ```table``` - the table to operate on

---

## *v.sys.start_dist_sends(database, table)*

Restart background data distribution for the specified table.

* Parameters
    * ```database``` - the database containing the table to operate on
    * ```table``` - the table to operate on

---

## *v.sys.stop_merges(database, table)*

Halt merge operations on the specified table.

* Parameters
    * ```database``` - the database containing the table to operate on
    * ```table``` - the table to operate on

---

## *v.sys.start_merges(database, table)*

Start/restart merge operations on the specified table.

* Parameters
    * ```database``` - the database containing the table to operate on
    * ```table``` - the table to operate on

---
