# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


class PosixStorage:
    URI = 'file'

    def __init__(self, filename):
        self.uri = filename

    @property
    def path(self):
        return self.uri.split('://', 1)[1]
