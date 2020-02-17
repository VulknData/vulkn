# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import logging


import vulkn.sql.utils as utils
import vulkn.sql.library as library
import vulkn.session as session
from vulkn.contrib.sqlparse import sqlparse


log = logging.getLogger()


class SQLStatement:
    def __init__(self, statement: str) -> None:
        self._original_statement = statement.strip(';').strip()

    def __str__(self) -> str:
        return self._original_statement

    def ASTAnalyzeRewrite(self) -> str:
        ast = sqlparse.parse(self._original_statement)[0]
        if ast.get_type() == 'SELECT':
            for ext in library.extensions.keys():
                ast = library.extensions[ext](ast)
        return ast

    def optimize(self):
        if session.enable_parser:
            return str(self.ASTAnalyzeRewrite())
        return self._original_statement