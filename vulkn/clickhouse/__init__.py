# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import subprocess
import os


def sqlformat(query, oneline=True, hilite=False):
    env = {'LC_ALL': 'C'}
    cmd = ['clickhouse-format']
    if oneline:
        cmd += ['--oneline']
    if hilite:
        cmd += ['--hilite']
    try:
        p = subprocess.run(cmd,
                           stdout=subprocess.PIPE,
                           input=query.strip().replace('\\', ''),
                           env=env,
                           encoding='ascii')
        if p.returncode != 0:
            raise Exception
    except:
        print(query.strip().replace('\\', ''))
        raise
    return str('{};'.format(p.stdout.strip()))


def net_list_tables(path):
    return os.listdir(path)


def net_list_parts(path, table):
    return [
        d for d in os.listdir('{path}/{table}'.format(path=path, table=table)) 
            if os.path.isdir('{path}/{table}/{d}'.format(path=path, table=table, d=d))
            and d != 'detached']


def net_list_detached(path, table):
    return os.listdir('{path}/{table}/detached'.format(path=path, table=table))


def net_show_schema(path, table):
    with open(f'{path}/{table}/{table}.sql', 'r') as f:
        return '{};'.format(''.join(f.readlines()).strip())
           

def net_attach(path, table):
    schema = net_show_schema(path, table)
    # create symlink
    # run query
    # execute schema query above


def net_archive(path, table):
    pass
    # detach table
    # copy data to fs
    # attach table
    # copy metadata to archive
    # drop table
