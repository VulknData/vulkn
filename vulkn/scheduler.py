# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only

import subprocess
import os
import logging
import multiprocessing as mp
from functools import partial


from vulkn.clickhouse import sqlformat
from vulkn.utils import singleton, LogLevels, timer


log = logging.getLogger()


try:
    mp.set_start_method('forkserver')
except:
    pass


def CLIExecutor(log, cli, query):
    p = subprocess.run(cli, input=query, stdout=subprocess.PIPE, universal_newlines=True)
    return p.returncode


@singleton
class VulknScheduler:
    # TODO: This is a very naive scheduler used by the MergeVectors only. Needs far more work.
    def __init__(self, ctx, threads=None):
        self._ctx = ctx
        self._conn = self._ctx._conn
        self._total_threads = os.cpu_count()
        self._usable_threads = threads or int(self._total_threads*0.75)
        self._pool = None

    def dispatch(self, query):
        if isinstance(query, list):
            if len(query) == 1:
                query = query[0]
            else:
                return self._dispatch_pool(query)
        if isinstance(query, str):
            return self._dispatch_single(query)
        raise Exception('Unknown parameter to exec')

    def _dispatch_single(self, query):
        return self._conn.execute(query) == 0

    def _dispatch_pool(self, queries):
        flag_opts_overrides = {'disable_suggestion': True}
        opts_overrides = {'format': 'TSVWithNamesAndTypes'}
        cli = self._conn._cli(flag_opts_overrides=flag_opts_overrides, 
                              opts_overrides=opts_overrides,
                              settings_overrides=None)
        executor = partial(CLIExecutor, log, cli)
        if self._pool is None:
            self._pool = mp.Pool(self._usable_threads)
        [log.log(LogLevels.SQL, q) for q in queries]
        r = sum(self._pool.map(executor, queries))
        return r == 0