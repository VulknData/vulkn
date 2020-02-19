# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import logging


from vulkn.contrib.sqlparse import sqlparse
import vulkn.sql.utils as utils


log = logging.getLogger()
__priority__ = 11


def ASTRewriteChunkByClause(ast):
    ret = sqlparse.parse(str(list(_rewrite(ast))[0]))[0]
    return ret

def _rewrite(ast):
    tree = ast.tokens if isinstance(ast, sqlparse.sql.TokenList) else ast
    for idx, token in enumerate(tree):
        if token.ttype == sqlparse.tokens.Keyword and token.value.upper().startswith('CHUNK'):
            yield _ASTRewriteChunkByClause(ast, ast, idx).rewrite()
            break
    else:
        yield ast

class _ASTRewriteChunkByClause():
    def __init__(self, tokens, ast, curr_idx):
        self._tokens = tokens.tokens
        self._ast = ast
        self._curr_idx = curr_idx

    def rewrite(self):
        args = utils.get_keyword_function_args(self._ast, self._curr_idx)
        (key, chunk_size) = (args[0], args[1])
        utils.del_keyword_function_node(self._tokens, self._ast, self._curr_idx)
        for j in range(0, len(self._ast.tokens)):
            if isinstance(self._ast[j], sqlparse.sql.Where):
                self._ast[j].tokens.append(sqlparse.sql.Token('Literal', ' AND ({chunk_clause})'))
                break
            if self._ast[j].ttype == sqlparse.tokens.Keyword and (
                    self._ast[j].value.upper().startswith('GROUP') or
                    self._ast[j].value.upper().startswith('ORDER') or
                    self._ast[j].value.upper().startswith('LIMIT')):
                self._ast.insert_before(j, sqlparse.sql.Token('Literal', ' '))
                self._ast.insert_before(j, sqlparse.sql.Token('Literal', '{chunk_clause}'))
                self._ast.insert_before(j, sqlparse.sql.Token('Literal', 'WHERE '))
                break
        else:
            self._ast.tokens.append(sqlparse.sql.Token('Literal', 'WHERE ({chunk_clause})'))
        chunk_clause = f'cityHash64({key})%{chunk_size}={{chunk_step}}'
        l = [
            ''.join(map(str, self._ast)).format(chunk_clause=chunk_clause.format(chunk_step=k))
            for k in range(0, int(chunk_size))]
        q = '\nUNION ALL\n'.join(s.strip() for s in l)
        return q
