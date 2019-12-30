# q(query)

The ```q``` method accepts an SQL query string and can be used to execute standard SQL queries against a ClickHouse or Workspace.

## Example

```python
v.q('select * from system.tables limit 1').show()
```
