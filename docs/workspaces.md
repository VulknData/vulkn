A Workspace is a defined ClickHouse environment and can be local or remote. It can be either a static
database, such as one instantiated and managed by your IT staff or dynamic/generated one (optionally 
temporary) that is created on demand by Vulkn itself.

Think of a Workspace as a place to define and optionally persist your data projects.

All Workspaces are stored within a Folio. Folios provide both namespaces and a storage base for 
dynamic, local Workspaces. Workspaces definitions are stored in a file - ```$USER/.vulkn/config.yaml``` 
under the ```folios``` key.

When Workspace is instantiated/defined a local instance of ClickHouse is started under the current 
user. This is coupled to the Python API, along with either temporary or permanent storage. Users can
nominate for either temporary or permanent Workspaces and manage their Workspaces via the vulkn CLI.
Permanent Workspaces can be thought of as private ClickHouse databases, complete with SQL interfaces,
persistent data and managed configuration. Multiple users can launch multiple Workspaces on a single 
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
2019.11.02 11:20:10.360520 [ 1 ] {} <Debug> ConfigReloader: Loading config '/tmp/ironman-e61897f1-b013-449f-a265-736b6c4e656c/etc/users.xml'
2019.11.02 11:20:10.360929 [ 1 ] {} <Information> Application: Loading metadata from /tmp/ironman-e61897f1-b013-449f-a265-736b6c4e656c/clickhouse/
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

You can also instantiate a temporary local Workspace directly within Python using Vulkn. The 
LocalWorkSpace object will automatically find free ports for the Native/TCP and HTTP ports and 
launch a private/local/temporary instance of ClickHouse for use by Vulkn. You can even run multiple 
instances of Vulkn with their own private Workspaces on a single machine.

```python
from vulkn import Vulkn
from vulkn.workspaces import LocalWorkSpace

v = Vulkn(workspace=LocalWorkSpace.tempWorkSpace())
```

### Persistent local Workspaces

A Workspace may also be persistent. This allows you to save data locally and pick up your investigation
at a later stage. You need to provide the --persist flag. It is highly recommended that you provide
a name as well.

```bash
(base) ironman@hulk ~$ vulkn --persist --local --name 'MyPersistentWorkspace'

2020.01.11 10:42:07.272906 [ 1 ] {} <Trace> Pipe: Pipe capacity is 1.00 MiB
2020.01.11 10:42:07.272996 [ 1 ] {} <Information> : Starting ClickHouse 20.1.1.2068 with revision 54431
2020.01.11 10:42:07.273059 [ 1 ] {} <Information> Application: starting up
2020.01.11 10:42:07.283007 [ 1 ] {} <Trace> Application: Will mlockall to prevent executable memory from being paged out. It may take a few seconds.
2020.01.11 10:42:07.307716 [ 1 ] {} <Trace> Application: The memory map of clickhouse executable has been mlock'ed
2020.01.11 10:42:07.307976 [ 1 ] {} <Debug> Application: Set max number of file descriptors to 1048576 (was 1024).
2020.01.11 10:42:07.307989 [ 1 ] {} <Debug> Application: Initializing DateLUT.
2020.01.11 10:42:07.307995 [ 1 ] {} <Trace> Application: Initialized DateLUT with time zone 'UTC'.
2020.01.11 10:42:07.309573 [ 1 ] {} <Debug> ConfigReloader: Loading config '/home/ironman/.vulkn/89f1012a-e3f5-4b97-b398-79a42e89d90a/vulkn/etc/users.xml'
2020.01.11 10:42:07.310056 [ 1 ] {} <Information> Application: Loading metadata from /home/ironman/.vulkn/89f1012a-e3f5-4b97-b398-79a42e89d90a/vulkn/clickhouse/
2020.01.11 10:42:07.310617 [ 1 ] {} <Information> DatabaseOrdinary (default): Total 0 tables and 0 dictionaries.
2020.01.11 10:42:07.310633 [ 1 ] {} <Information> DatabaseOrdinary (default): Starting up tables.
2020.01.11 10:42:07.310684 [ 1 ] {} <Debug> Application: Loaded metadata.
2020.01.11 10:42:07.310698 [ 1 ] {} <Information> BackgroundSchedulePool: Create BackgroundSchedulePool with 16 threads
2020.01.11 10:42:07.312834 [ 1 ] {} <Information> Application: Listening for http://[::1]:8124
2020.01.11 10:42:07.312930 [ 1 ] {} <Information> Application: Listening for connections with native protocol (tcp): [::1]:9001
2020.01.11 10:42:07.312993 [ 1 ] {} <Information> Application: Listening for http://127.0.0.1:8124
2020.01.11 10:42:07.313037 [ 1 ] {} <Information> Application: Listening for connections with native protocol (tcp): 127.0.0.1:9001
2020.01.11 10:42:07.313407 [ 1 ] {} <Information> Application: Available RAM: 62.60 GiB; physical cores: 8; logical cores: 16.
2020.01.11 10:42:07.313448 [ 1 ] {} <Information> Application: Ready for connections.

Добро пожаловать to VULKИ version 19.0.1!

██╗   ██╗██╗   ██╗██╗     ██╗  ██╗███╗   ██╗
██║   ██║██║   ██║██║     ██║ ██╔╝████╗  ██║
██║   ██║██║   ██║██║     █████╔╝ ██╔██╗ ██║
╚██╗ ██╔╝██║   ██║██║     ██╔═██╗ ██║╚██╗██║
 ╚████╔╝ ╚██████╔╝███████╗██║  ██╗██║ ╚████║
  ╚═══╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝                    

ClickHouse - an analytics database for the 21st century.

VULKИ entrypoint initialized as 'v'.
```

In the example above note how the Workspace is now instantiated under '/home/ironman/.vulkn/89f1012a-e3f5-4b97-b398-79a42e89d90a'
instead of /tmp.

Workspace names in a Folio are not unique and you have to specify the full path to the Workspace to
re-instantiate it.

```bash
(base) ironman@hulk ~$ vulkn --persist --local --workspace /home/ironman/.vulkn/89f1012a-e3f5-4b97-b398-79a42e89d90a
```

You can also work with persistent Workspaces programmatically:

```python
from vulkn import Vulkn
from vulkn.workspaces import LocalWorkSpace

v = Vulkn(workspace=LocalWorkSpace(persist=True, workspace='/home/ironman/.vulkn/89f1012a-e3f5-4b97-b398-79a42e89d90a'))
```

## Remote Instances

You can use the ```vulkn``` CLI command to connect to remote ClickHouse instances by 
providing the hostname, port and credentials. Note that you must have write privileges to the remote 
'vulkn' database to store cached objects and other session metadata.

```bash
(base) ironman@hulk ~$ vulkn --host baby.yoda.net --user mando --password thermaldetenator --port 9000
Добро пожаловать to VULKИ version 19.0.1!

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

You can connect to remote instance programmatically with the Vulkn object directly as well:

```python
from vulkn import Vulkn

v = Vulkn(host='baby.yoda.net', port=9000, user='mando', password='thermaldetenator')
```

## Managing Folios and Workspaces

TODO: Provide more information here.

```
vulkn --help
usage: - [-h] [--list-folios] [--persist] [--local] [--save-auth]
         [--name NAME] [--folio FOLIO] [--workspace WORKSPACE] [--host HOST]
         [--user USERNAME] [--password PASSWORD] [--port PORT]
         [--log-level LOGLEVEL] [--timing]

vulkn

optional arguments:
  -h, --help            show this help message and exit
  --list-folios
  --persist
  --local
  --save-auth
  --name NAME
  --folio FOLIO
  --workspace WORKSPACE
  --host HOST
  --user USERNAME
  --password PASSWORD
  --port PORT
  --log-level LOGLEVEL
  --timing
```
