# Workspaces

A Workspace is a defined ClickHouse environment and can be local or remote, static, dynamic or temporary. 
Think of a Workspace as a place to define and optionally persist your data projects.

All Workspaces are stored within a Folio. Folios provide both namespaces and a storage base for 
dynamic, local Workspaces. Workspaces definitions are stored in a file - ```$USER/.vulkn/config.yaml``` 
under the ```folios``` key.


When Workspace is instantiated/defined a local instance of ClickHouse is started under the current 
user. This is coupled to the Python API, along with either temporary or permanent storage. Users can
nominate for either temporary or permanent workspaces and manage their workspaces via the vulkn CLI.
Permanent workspaces can be thought of as private ClickHouse databases, complete with SQL interfaces,
persistent data and managed configuration. Multiple users can launch multiple workspaces on a single 
machine if desired.

## Local Workspaces

### Temporary local Workspaces

When using the ```vulkn``` CLI use the ```--local``` option to create and start a local temporary 
Workspace. This will create the relevant directories and configuration files in a directory in ```/tmp```
and start a ClickHouse instance pointing towards this configuration and storage. You can use Vulkn 
and ClickHouse as if it was a fully-featured ClickHouse instance including disk and memory storage 
options. All data will be deleted/removed when you exit Vulkn.

```text
(base) ironman@hulk ~$ vulkn --local

2019.11.02 11:20:10.336121 [ 1 ] {} <Information> : Starting ClickHouse 19.17.1.1589 with revision 54428
2019.11.02 11:20:10.336179 [ 1 ] {} <Information> Application: starting up
2019.11.02 11:20:10.338372 [ 1 ] {} <Trace> Application: Will mlockall to prevent executable memory from being paged out. It may take a few seconds.
2019.11.02 11:20:10.358519 [ 1 ] {} <Trace> Application: The memory map of clickhouse executable has been mlock'ed
2019.11.02 11:20:10.358679 [ 1 ] {} <Debug> Application: Set max number of file descriptors to 1048576 (was 1024).
2019.11.02 11:20:10.358687 [ 1 ] {} <Debug> Application: Initializing DateLUT.
2019.11.02 11:20:10.358690 [ 1 ] {} <Trace> Application: Initialized DateLUT with time zone 'UTC'.
2019.11.02 11:20:10.360520 [ 1 ] {} <Debug> ConfigReloader: Loading config '/tmp/jason-e61897f1-b013-449f-a265-736b6c4e656c/etc/users.xml'
2019.11.02 11:20:10.360929 [ 1 ] {} <Information> Application: Loading metadata from /tmp/jason-e61897f1-b013-449f-a265-736b6c4e656c/clickhouse/
2019.11.02 11:20:10.361442 [ 1 ] {} <Information> DatabaseOrdinary (default): Total 0 tables and 0 dictionaries.
2019.11.02 11:20:10.361451 [ 1 ] {} <Information> DatabaseOrdinary (default): Starting up tables.
2019.11.02 11:20:10.361499 [ 1 ] {} <Debug> Application: Loaded metadata.
2019.11.02 11:20:10.361509 [ 1 ] {} <Information> BackgroundSchedulePool: Create BackgroundSchedulePool with 16 threads
2019.11.02 11:20:10.363225 [ 1 ] {} <Information> Application: Listening http://[::1]:8124
2019.11.02 11:20:10.363244 [ 1 ] {} <Information> Application: Listening for connections with native protocol (tcp): [::1]:9001
2019.11.02 11:20:10.363262 [ 1 ] {} <Information> Application: Listening http://127.0.0.1:8124
2019.11.02 11:20:10.363274 [ 1 ] {} <Information> Application: Listening for connections with native protocol (tcp): 127.0.0.1:9001
2019.11.02 11:20:10.363412 [ 1 ] {} <Information> Application: Available RAM: 62.60 GiB; physical cores: 8; logical cores: 16.
2019.11.02 11:20:10.363416 [ 1 ] {} <Information> Application: Ready for connections.

Добро пожаловать to VULKИ version 2019.1.1!

██╗   ██╗██╗   ██╗██╗     ██╗  ██╗███╗   ██╗
██║   ██║██║   ██║██║     ██║ ██╔╝████╗  ██║
██║   ██║██║   ██║██║     █████╔╝ ██╔██╗ ██║
╚██╗ ██╔╝██║   ██║██║     ██╔═██╗ ██║╚██╗██║
 ╚████╔╝ ╚██████╔╝███████╗██║  ██╗██║ ╚████║
  ╚═══╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝                    

Stop waiting for your queries to complete and start having fun.

VULKИ entrypoint initialized as 'v'.

>>> 
```

You can also instantiate 

```python
from vulkn.workspaces import LocalWorkSpace
from vulkn.utils import get_next_free_socket

port = get_next_free_socket('127.0.0.1', list(range(9001,10000))),
http_port = get_next_free_socket('127.0.0.1', list(range(8124,10000))))

w = LocalWorkSpace(persist=False, port=port, http_port=http_port)
atexit.register(w.stop)
v = vulkn.Vulkn(port=port)
```

### Persistent local Workspaces

## Remote Workspaces

## Managing Folios and Workspaces


Folios are 

Under the hood 
a Workspace is a place where data scientists and developers can develop, play with data or store a project

A workspace consists of a stand-alone, local instance of the ClickHouse server. When a workspace is instantiated a local instance of ClickHouse is started under the current user. This is coupled to the Python API, along with either temporary or permanent storage. Users can nominate for either temporary or permanent workspaces and manage their workspaces via the vulkn CLI. Permanent workspaces can be thought of as a private ClickHouse databases, complete with SQL interfaces, persistent data and managed configuration. Multiple users can launch multiple workspaces on a single machine if desired.

    Workspaces will be extended in the future to offer both local and remote storage with the ability to pull in datasets from remote databases and systems for analysis within the local instance.