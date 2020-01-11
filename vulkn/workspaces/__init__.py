# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import getpass
import os
import yaml
import uuid
import shutil
import subprocess
import time
import pathlib
import atexit


from vulkn.config import VulknConfig
from vulkn.clickhouse.client.cli import ClickHouseCLIClient
from vulkn.utils import get_next_free_socket


templates = '{}/templates'.format(pathlib.Path(__file__).parent.absolute())
CONFIG_TEMPLATE = open(f'{templates}/config.xml').read()
USERS = open(f'{templates}/users.xml').read()


class UserWorkSpaceManager():
    def __init__(self):
        self._username = getpass.getuser()
        self._config_dir = '{}/.vulkn'.format(os.path.expanduser('~'))
        os.makedirs(self._config_dir + '/default', 0o700, exist_ok=True)
        if not os.path.exists(self._config_dir + '/config.yaml'):
            config = {
                'folios': {
                    self._config_dir + '/default': []
                }
            }
            open(self._config_dir + '/config.yaml', 'w').write(yaml.dump(config))

    def get_config(self):
        return yaml.load(open(self._config_dir + '/config.yaml').read(), Loader=yaml.FullLoader)

    def add_workspace(self, uuid: str, workspace: str, folio: str='default', name: str=None):
        config = self.get_config()
        if folio == 'default' or folio is None:
            folio = self._config_dir + '/default'
        if folio in config['folios']:
            for w in config['folios'][folio]:
                if uuid == w['uuid']:
                    return
        config['folios'].setdefault(folio, []).append(
            {'name': name or '', 'uuid': str(uuid), 'workspace': workspace})
        open(self._config_dir + '/config.yaml', 'w').write(yaml.dump(config))

    def remove_workspace(self, uuid: str):
        config = self.get_config()
        for k, v in config['folios'].items():
            config['folios'][k] = [i for i in v if i['uuid'] != uuid]
        open(self._config_dir + '/config.yaml', 'w').write(yaml.dump(config))

    def save_auth(self, server: str, username: str):
        password = getpass.getpass(prompt='Password: ', stream=None) 
        config = self.get_config()
        config.setdefault('auth', {})[server] = {'username': username, 'password': password}
        open(self._config_dir + '/config.yaml', 'w').write(yaml.dump(config))

    def get_workspace(self, workspace, folio, persist):
        uuid_str = None
        if (workspace and os.path.exists(workspace)):
            uuid_str = open(workspace + '/vulkn/uuid').read().strip()
        else:
            uuid_str = str(uuid.uuid4())
        if persist:
            if (folio is None or folio == 'default') and workspace is None:
                workspace = self._config_dir + '/' + uuid_str
        else:
            if workspace is None:
                workspace = '/tmp/{}-{}'.format(getpass.getuser(), uuid_str)
        return (workspace, uuid_str)


class LocalWorkSpace():
    def __init__(self,
                 workspace: str=None,
                 folio: str=None,
                 name: str=None,
                 persist: bool=False,
                 http_port=None,
                 port=None,
                 overwrite=False,
                 timeout=10):
        if port is None:
            port = get_next_free_socket('127.0.0.1', list(range(9001,10000)))
        if http_port is None:
            http_port = get_next_free_socket('127.0.0.1', list(range(8124,8999)))
        self._workspace, self._uuid = UserWorkSpaceManager().get_workspace(workspace, folio, persist)
        self._folio = folio
        self._name = name
        self._persist = persist
        self._timeout = timeout
        self._port = port
        self._http_port = http_port
        self._service = None
        self._config = {
            'log_file': f'{self._workspace}/vulkn/logs/clickhouse-server.log',
            'error_log_file': f'{self._workspace}/vulkn/logs/clickhouse-server.err.log',
            'session_name': 'vulkn',
            'http_port': str(http_port),
            'tcp_port': str(port),
            'data_directory': f'{self._workspace}/vulkn/clickhouse',
            'tmp_directory': f'{self._workspace}/vulkn/clickhouse/tmp',
            'user_files_directory': f'{self._workspace}/vulkn/user_files',
            'format_schema_directory': f'{self._workspace}/vulkn/schemas'
        }

        if os.path.exists(self._workspace):
            if overwrite:
                self._cleanup()
        else:
            os.makedirs(self._workspace, 0o777, exist_ok=False)
            dirs = ['build', 'cores', 'data', 'dictionaries_lib', 'flags', 'format_schemas',
                    'metadata', 'preprocessed_configs', 'storage', 'tmp', 'user_files']
            for d in dirs:
                os.makedirs(f'{self._workspace}/vulkn/clickhouse/{d}', 0o777, exist_ok=True)

        os.makedirs(f'{self._workspace}/vulkn/etc', 0o777, exist_ok=True)

        uuid_info = open(f'{self._workspace}/vulkn/uuid', 'w')
        uuid_info.write(str(self._uuid) + '\n')
        uuid_info.close()

        conf = open(f'{self._workspace}/vulkn/etc/config.xml', 'w')
        conf.write(CONFIG_TEMPLATE.format(**self._config))
        conf.close()

        users = open(f'{self._workspace}/vulkn/etc/users.xml', 'w')
        users.write(USERS)
        users.close()

        self.start()
        atexit.register(self.stop)

    @classmethod
    def tempWorkSpace(cls, path=None):
        w = cls(persist=False, workspace=path)
        return w

    def start(self):
        server = ['clickhouse-server', 
                  '-C', f'{self._workspace}/vulkn/etc/config.xml',
                  '-P', f'{self._workspace}/vulkn/clickhouse.pid']
        self._service = subprocess.Popen(server, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        for i in range(0, self._timeout):
            time.sleep(0.1)
            try:
                log_data = open(f'{self._workspace}/vulkn/logs/clickhouse-server.log', 'r').read()
                if 'Ready for connections' in log_data:
                    cx = ClickHouseCLIClient().setAuth(host='localhost', port=self._config['tcp_port'])
                    cx.execute('CREATE DATABASE IF NOT EXISTS {}'.format(VulknConfig['tmp']))
                    err_log = open(f'{self._workspace}/vulkn/logs/clickhouse-server.err.log', 'r').read()
                    print(err_log)
                    print(log_data)
                    break
            except:
                pass

        if self._persist:
            UserWorkSpaceManager().add_workspace(self._uuid, self._workspace, self._folio, self._name)

    def _cleanup(self):
        shutil.rmtree(f'{self._workspace}/vulkn')
        if not os.listdir(self._workspace):
            os.rmdir(self._workspace)

    def stop(self):
        self._service.terminate()
        try:
            outs, _ = self._service.communicate(timeout=self._timeout)
            print('Exit code', self._service.returncode)
            print(outs.decode('utf-8'))
        except subprocess.TimeoutExpired:
            print('subprocess did not terminate in time')
        if not self._persist:
            self._cleanup()
        else:
            os.rename(
                f'{self._workspace}/vulkn/logs/clickhouse-server.log',
                '{}/vulkn/logs/clickhouse-server.log.{}'.format(self._workspace, str(int(time.time()))))
            os.rename(
                f'{self._workspace}/vulkn/logs/clickhouse-server.err.log',
                '{}/vulkn/logs/clickhouse-server.err.log.{}'.format(self._workspace, str(int(time.time()))))
