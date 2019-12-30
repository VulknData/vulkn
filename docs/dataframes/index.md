# DataFrames

DataFrames are specialised container objects that can refer to either tables or queries including queries comprised of other DataFrames or tables in the form of subselects and joins. Vulkn provides a number of DataFrame entrypoints.

- q - SQL string interface.
- table/select - ORM/'SparkSQL-like' interface.
- one - table function interface to system.one.
- range - variant on the numbers DataFrame that allows negative start/end positions.
- numbers - interface to system.numbers, system.numbers_mt and the table functions numbers(), numbers_mt().
- update - updating table DataFrame.
- delete - delete table DataFrame.
