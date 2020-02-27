# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import random
import sys
import pprint
import argparse
import atexit
import logging


import vulkn
import vulkn.funcs as funcs
import vulkn.engines as engines
from vulkn.workspaces import UserWorkSpaceManager, LocalWorkSpace
from vulkn.funcs import and_, or_, not_, xor_, if_, multiIf, switch
from vulkn.types import *
from vulkn.utils import get_next_free_socket
from vulkn.datatable import WriteMode, JoinStrictness
from vulkn.config import VERSION


log = logging.getLogger()
log.setLevel('INFO')
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

parser = argparse.ArgumentParser(description='vulkn')

parser.add_argument('--list-folios', action='store_true')
parser.add_argument('--persist', action='store_true')
parser.add_argument('--local', action='store_true', default=False)
parser.add_argument('--save-auth', action='store_true')
parser.add_argument('--name', metavar='NAME', default=None)
parser.add_argument('--folio', metavar='FOLIO', default=None)
parser.add_argument('--workspace', metavar='WORKSPACE', default=None)
parser.add_argument('--host', metavar='HOST', default='localhost')
parser.add_argument('--user', metavar='USERNAME', default='default')
parser.add_argument('--password', metavar='PASSWORD', default='')
parser.add_argument('--port', metavar='PORT', default='9000')
parser.add_argument('--http_port', metavar='HTTP_PORT', default='8123')
parser.add_argument('--log-level', metavar='LOGLEVEL', default='INFO')
parser.add_argument('--timing', action='store_true')
parser.add_argument('--client', metavar='CLIENT', default='cli')

args = parser.parse_args()

if args.list_folios:
    pprint.pprint(UserWorkSpaceManager().get_config())
    sys.exit(0)

if args.save_auth:
    if args.save_auth and args.server and args.user:
        UserWorkSpaceManager().save_auth(args.server, args.user)
    else:
        print('Authentication not set')
        sys.exit(1)
    sys.exit(0)

ce = None
if args.local:
    args.port = get_next_free_socket('127.0.0.1', list(range(9001,10000)))
    args.http_port = get_next_free_socket('127.0.0.1', list(range(8124,8999)))
    ce = LocalWorkSpace(persist=args.persist,
                        name=args.name,
                        workspace=args.workspace,
                        folio=args.folio,
                        port=args.port,
                        http_port=args.http_port)

v = vulkn.Vulkn(host=args.host, port=args.port, http_port=args.http_port, user=args.user, password=args.password, client=args.client)

vulkn.session.log.setLevel(args.log_level)
vulkn.session.timing = args.timing

tags = [
    "The environmentally friendly real-time analytics engine powered by ClickHouse.",
    "The developer friendly real-time analytics engine powered by ClickHouse.",
    "Stop waiting for your queries to complete and start having fun.",
    "ClickHouse - an analytics database for the 21st century."
]

print(f"""Copyright (C) 2019,2020 Jason Godden / VulknData Pty Ltd.

Добро пожаловать to VULKИ version {VERSION}!

██╗   ██╗██╗   ██╗██╗     ██╗  ██╗███╗   ██╗
██║   ██║██║   ██║██║     ██║ ██╔╝████╗  ██║
██║   ██║██║   ██║██║     █████╔╝ ██╔██╗ ██║
╚██╗ ██╔╝██║   ██║██║     ██╔═██╗ ██║╚██╗██║
 ╚████╔╝ ╚██████╔╝███████╗██║  ██╗██║ ╚████║
  ╚═══╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝                    
""")

print(tags[random.randint(0, len(tags)-1)])
print("\nVULKИ entrypoint initialized as 'v'.\n")
