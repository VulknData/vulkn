# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import logging
from typing import List


from vulkn.contrib.sqlparse import sqlparse
from vulkn.sql.statement import SQLStatement


log = logging.getLogger()


class SQLMessage:
    def __init__(self, message: str) -> None:
        self._original_message = message

    def statements(self) -> List:
        return [SQLStatement(s) for s in sqlparse.split(self._original_message)]

    @property
    def original_message(self) -> str:
        return self._original_message

    def __str__(self) -> str:
        return '\n'.join([str(s) for s in self.statements()])
