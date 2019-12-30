#!/usr/bin/env python

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import vulkn
from vulkn.workspaces import LocalWorkSpace

ws = LocalWorkSpace(persist=False)
v = vulkn.Vulkn(host='localhost', port=9001)

all_funcs = v.table('system.functions').select('*').orderBy('is_aggregate', 'name')
funcs = all_funcs.where('not is_aggregate').exec().to_records()
agg_funcs = all_funcs.where('is_aggregate').exec().to_records()

for f in funcs:
    print(f"{f['name']},{f['alias_to']}")
#print(agg_funcs)

ws.stop()