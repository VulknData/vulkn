# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from fixtures import v
from vulkn.datatable import WriteMode
from vulkn.types import *
import vulkn.funcs.encode as encode


def test_datatable_select_str_expression(v):
    df = v.select(c(encode.hex(String('123'))).alias('foo'))
    assert df.exec().to_records() == [{'foo':313233}]

