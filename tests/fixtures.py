# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import pytest


@pytest.fixture(scope='module')
def v():
    import vulkn
    from vulkn.workspaces import LocalWorkSpace

    ws = LocalWorkSpace(persist=False)
    f = vulkn.Vulkn(host='localhost', port=9001)
    f._port = 9001
    f._reload()
    yield f
    del f
    ws.stop()
