# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import logging


import vulkn.sql.library as vlib
from vulkn.contrib.sqlparse import sqlparse


log = logging.getLogger()
__priority__ = 1


def ASTRewriteUserDefinedFunctions(ast):
    ret = sqlparse.parse(str(sqlparse.sql.TokenList(list(_rewrite(ast)))))[0]
    return ret

def _rewrite(ast):
    tree = ast.tokens if isinstance(ast, sqlparse.sql.TokenList) else ast
    for idx, token in enumerate(tree):
        if isinstance(token, sqlparse.sql.Parenthesis):
            if len(token.tokens) > 1 or not isinstance(token.tokens[0], sqlparse.sql.Token):
                for t in _rewrite(token):
                    yield t
            else:
                yield token
        elif isinstance(token, sqlparse.sql.Function):
            if token.tokens[0].value in vlib.udfs.keys():
                parameters = _rewrite(token.get_parameters())
                yield sqlparse.sql.Token(
                    sqlparse.tokens.Literal,
                    vlib.udfs[token.tokens[0].value](*list(parameters)))
            else:
                yield token
        elif isinstance(token, sqlparse.sql.Identifier):
            if len(token.tokens) > 1 or not isinstance(token.tokens[0], sqlparse.sql.Token):
                for t in _rewrite(token):
                    yield t
            else:
                yield token
        elif isinstance(token, sqlparse.sql.IdentifierList):
            for t in _rewrite(token):
                yield t
        else:
            yield token
