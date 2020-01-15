# System Management

The following system functions can be used to manage internal system processors, dictionaries, caches and
distributed operations.

ClickHouse reference - https://clickhouse.yandex/docs/en/query_language/system/

---

## *v.sys.reloadDicts()*

Reload all currently LOADED dictionaries.

---

## *v.sys.reloadDict(dictionary)*

Reload or load a specific dictionary.

* Parameters
    * ```dictionary``` - the name of the dictionary to reload

---

## *v.sys.dropDNSCache()*

Reset ClickHouse's internal DNS cache.

---

## *v.sys.dropMarkCache()*

Reset the mark cache (useful for performance testing).

---

## *v.sys.flushLogs()*

Flush logs to the system tables.

---

## *v.sys.reloadConfig()*

Reload the ClickHouse configuration.

---

## *v.sys.shutdown()*

Shuts down the database instance. Note this will terminate your Vulkn instance.

---

## *v.sys.kill()*

Force kill the database instance (and your Vulkn session).

---

## *v.sys.stopDistSends(database, table)*

Disable background data distribution for the specified table.

* Parameters
    * ```database``` - the database containing the table to operate on
    * ```table``` - the table to operate on

---

## *v.sys.flushDist(database, table)*

Flush all data to the cluster nodes synchronously.

* Parameters
    * ```database``` - the database containing the table to operate on
    * ```table``` - the table to operate on

---

## *v.sys.startDistSends(database, table)*

Restart background data distribution for the specified table.

* Parameters
    * ```database``` - the database containing the table to operate on
    * ```table``` - the table to operate on

---

## *v.sys.stopMerges(database, table)*

Halt merge operations on the specified table.

* Parameters
    * ```database``` - the database containing the table to operate on
    * ```table``` - the table to operate on

---

## *v.sys.startMerges(database, table)*

Start/restart merge operations on the specified table.

* Parameters
    * ```database``` - the database containing the table to operate on
    * ```table``` - the table to operate on

---
