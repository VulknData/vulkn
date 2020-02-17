# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import pprint
import logging
import itertools
from typing import List
from functools import wraps


from vulkn.contrib.sqlparse import sqlparse


log = logging.getLogger()


def validate_parameters(*args):
    safe_tokens = set([sqlparse.tokens.Name])
    for a in args:
        if hasattr(a, 'tokens'):
            if not set([t.ttype for t in a.tokens]).issubset(safe_tokens):
                return False
    return True


# TODO: This function protects against SQL injection as far as Vulkn UDFs and other internal query
# rewriting is concerned however as the Vulkn SQL engine is a second level engine it doesn't handle
# cases where users manually construct poisonous strings which are used to build a query. In this
# case the SQL injection is present *before* it is submitted to the Vulkn rewriter. A future Vulkn 
# SQL Server will handle SQL injection (as it will be responsible for building the query at that
# point however is out of scope for the initial release).
def ast_protect_injection(function):
    @wraps(function)
    def protected_call(*args):
        if not validate_parameters(*args):
            raise Exception('Cancelling due to potential SQL injection')
        return function(*args)
    return protected_call


def ast_where_clause(ast):
    (idx, where_clause) = ast.token_next_by(i=sqlparse.sql.Where)
    return where_clause


def ast_from_clause(ast):
    for idx, token in enumerate(ast):
        if token.ttype == sqlparse.tokens.Keyword and token.normalized == 'FROM':
            return ast.token_next(idx)[1]
    else:
        return None


def ast_column_projections(ast):
    (start_idx, ident_list) = ast.token_next_by(i=sqlparse.sql.IdentifierList)
    return list(ident_list.get_identifiers())


def get_keyword_function_args(q, start_idx: int) -> List:
    arg_clause = [l for l in q[start_idx+1:] if not l.is_whitespace][0]
    return list(map(str, list(arg_clause[1].get_identifiers())))


def del_keyword_function_node(tokens, q, start_idx: int) -> str:
    for i in range(start_idx, len(q.tokens)):
        if q[i].is_group:
            del tokens[i]
            break
        else:
            del tokens[i]
    return str(q).strip()


def validate_statement_excludes(excludes, statement) -> tuple:
    funcs = lambda tk: sqlparse.utils.imt(tk, m=[(sqlparse.tokens.Keyword, e) for e in excludes])
    return statement._token_matching(funcs) == (None, None)
   

def get_functions(tokens):
    if isinstance(tokens, sqlparse.sql.Function):
        yield tokens[0].value
    for idx, token in enumerate(tokens):
        if isinstance(token, sqlparse.sql.Function):
            yield token[0].value
        if token.is_group:
            for g in get_functions(token):
                yield g


def get_identifiers(tokens):
    for idx, token in enumerate(tokens):
        if isinstance(token, sqlparse.sql.Identifier) and type(token.parent) != sqlparse.sql.Function:
            yield token[0].value
        if token.is_group:
            for g in get_identifiers(token):
                yield g


def resolve_identifiers(identifiers):
    ids = []
    seq = itertools.count(1)
    for l in identifiers:
        if type(l) == sqlparse.sql.Token:
            ids.append({'node': l, 'src': [], 'funcs': [], 'id': l.value})
        else:
            if len(l.tokens) == 1:
                ids.append({'node': l, 'src': [l.value], 'funcs': [], 'id': l.get_real_name()})
            else:
                node = {'node': l, 'id': l.get_alias() or str(l)}
                node['src'] = list(set(filter(lambda x: x != node['id'], get_identifiers(l))))
                node['funcs'] = list(set(list(get_functions(l))))
                ids.append(node)
    log.debug(ids)
    return ids
