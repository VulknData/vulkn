#!/usr/bin/env python

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import re
import vulkn

vulkn.session.log.setLevel('DEBUG')

v = vulkn.Vulkn(host='localhost', http_port=8123, client='http')

k = None

def get_parameter_count(msg):
    if 'requires at least' in msg:
        return (1,None,)
    m = re.match(r'.* passed (.*?), should be (.*?) or (.*?)\. \(', msg)
    if m is None:
        m = re.match(r'.* passed (.*?), should be (.*?) \(', msg)
        return (int(m[2]),0)
    return (int(m[2]), int(m[3]))

all_funcs = v.table('system.functions').select('name').orderBy('is_aggregate', 'name')
funcs = all_funcs.where('not is_aggregate').limit(40).exec().to_records()
agg_funcs = all_funcs.where('is_aggregate').exec().to_records()

for f in funcs:
    fname = f['name']
    print(fname)
    try:
        k = v.q(f'SELECT toTypeName({fname}()) AS t').r[0]['t']
    except Exception as e:
        # print(str(e))
        try:
            print(str(e))
            print(get_parameter_count(str(e)))
        except Exception as l:
            print(l)

print(k)
