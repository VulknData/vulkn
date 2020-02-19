# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import itertools
import logging
import textwrap


import vulkn.sql.utils as utils
import vulkn.sql.library as vlib
from vulkn.contrib.sqlparse import sqlparse


log = logging.getLogger()
__priority__ = 10


def ASTRewriteVectorizeByClause(ast):
    ret = sqlparse.parse(str(list(_AnalyzeVectorizeByAST(ast))[0]))[0]
    return ret


def _AnalyzeVectorizeByAST(ast):
    original_tree = ast.tokens if isinstance(ast, sqlparse.sql.TokenList) else ast
    current_tree = []
    subquery_found = False
    vectorize_found_idx = 0
    for idx, token in enumerate(original_tree):
        if subquery_found and isinstance(token, sqlparse.sql.Parenthesis):
            t = sqlparse.sql.TokenList(
                list(_AnalyzeVectorizeByAST(sqlparse.sql.TokenList(token.tokens[1:-1]))))
            current_tree.append(sqlparse.sql.Token('Literal', f' ({t}) '))
            subquery_found = False
            continue
        elif token.ttype == sqlparse.tokens.Keyword:
            if token.normalized == 'FROM' or 'JOIN' in token.normalized:
                if isinstance(ast.token_next(idx)[1], sqlparse.sql.Parenthesis):
                    subquery_found = True
            elif token.value.upper().startswith('VECTORIZE'):
                vectorize_found_idx = idx
        current_tree.append(token)
    a = sqlparse.sql.TokenList(current_tree)
    if vectorize_found_idx > 0:
        yield _VectorizeByASTRewriter(a, vectorize_found_idx).rewrite()
    else:
        yield a


def _RewriteVectorFunctionAST(ast):
    if isinstance(ast, sqlparse.sql.Function):
        if ast.tokens[0].value in vlib.vectors.keys():
            parameters = _RewriteVectorFunctionAST(ast.get_parameters())
            yield vlib.vectors[ast.tokens[0].value](*list(parameters))                
        else:
            yield token
    tree = ast.tokens if isinstance(ast, sqlparse.sql.TokenList) else ast
    for idx, token in enumerate(tree):
        if isinstance(token, sqlparse.sql.Parenthesis):
            if len(token.tokens) > 1 or not isinstance(token.tokens[0], sqlparse.sql.Token):
                for t in _RewriteVectorFunctionAST(token):
                    yield t
            else:
                yield token
        elif isinstance(token, sqlparse.sql.Function):
            if token.tokens[0].value in vlib.vectors.keys():
                parameters = _RewriteVectorFunctionAST(token.get_parameters())
                yield vlib.vectors[token.tokens[0].value](*list(parameters))                
            else:
                yield token
        elif isinstance(token, sqlparse.sql.Identifier):
            if len(token.tokens) > 1 or not isinstance(token.tokens[0], sqlparse.sql.Token):
                for t in _RewriteVectorFunctionAST(token):
                    yield t
            else:
                yield token
        elif isinstance(token, sqlparse.sql.IdentifierList):
            for t in _RewriteVectorFunctionAST(token):
                yield t
        else:
            yield token


class _VectorizeByASTRewriter():
    def __init__(self, ast, curr_idx):
        self._tokens = ast
        self._ast = ast
        self._curr_idx = curr_idx

    def rewrite(self):
        self.validate()
        p = self._parse()
        q = self._compile(
            p['from_clause'],
            p['where_clause'],
            p['key'],
            p['sort'],
            p['cols'],
            p['chunk_size'],
            p['metrics'],
            p['vectors'],
            p['expr']
        )
        return sqlparse.parse(q)[0]

    def validate(self):
        excludes = ['GROUP BY', 'ORDER BY', 'LIMIT BY', 'LIMIT']
        if not utils.validate_statement_excludes(excludes, self._ast):
            raise Exception('GROUP BY, ORDER BY, LIMIT BY and LIMIT are invalid in VECTORIZE BY statements')

    def _parse(self):
        def _parse_identifiers(ids, key, sort, cols):
            metrics = []
            vectors = []
            expr = []
            for id in utils.resolve_identifiers(ids):
                if len(set(vlib.vectors.keys()).intersection(set(id['funcs']))) > 0:
                    vectors.append(id)
                elif id['id'] != key and id['id'] != sort:
                    expr.append(id)
                for src in id['src']:
                    if not (src == key or src == sort or src in cols):
                        metrics.append(id)
            return (metrics, vectors, expr)
    
        args = utils.get_keyword_function_args(self._ast, self._curr_idx)
        # TODO: Chunking. Default to 1.
        # (key, sort, cols) = (args[0], args[-2], args[1:-2] if len(args) > 3 else [])
        (key, sort, cols) = (args[0], args[-1], args[1:-1] if len(args) > 3 else [])
        (metrics, vectors, expr) = _parse_identifiers(utils.ast_column_projections(self._ast), key, sort, cols)

        r = {    
            'from_clause': utils.ast_from_clause(self._ast),
            'where_clause': utils.ast_where_clause(self._ast),
            'key': key,
            'sort': sort,
            'cols': cols,
            # TODO: Chunking. Default to 1.
            #'chunk_size': int(args[-1]) if args[-1].isnumeric() else 2,
            'chunk_size': 1,
            'metrics': metrics,
            'vectors': vectors,
            'expr': expr
        }

        return r

    def _compile(self, from_clause, where_clause, key, sort, cols, chunk_size, metrics, vectors, expr):
        vector_funcs = [list(_RewriteVectorFunctionAST(f['node'])) for f in vectors]
        expr_cols = list([str(f['node']) for f in expr])
        metric_ids = list(set(list(itertools.chain.from_iterable([m['src'] for m in metrics]))))
        metric_map = dict((metric, idx+2) for idx, metric in enumerate(metric_ids))
        w = where_clause if where_clause is not None else ''
        # TODO: String replacement is hacky.
        aj_metric_vectors = list(itertools.chain.from_iterable(list(vf)[0][1] for vf in vector_funcs))
        for i, _ in enumerate(aj_metric_vectors):
            for k, v in metric_map.items():
                aj_metric_vectors[i] = aj_metric_vectors[i].replace(f'__{k}', f'`--#v`.{v}')
        metric_vector_aliases = itertools.chain(
            ['`--#v`.1 AS `{0}`'.format(sort)],
            [f'`--#v`.{v} AS `{k}`' for k, v in metric_map.items()],
            aj_metric_vectors)
        vector_aggs = [str(vector_funcs[i][0][0]) + ' AS ' + vectors[i]['id'] for i in range(len(vector_funcs))]
        query_template = textwrap.dedent("""\
            SELECT
                {final_projection},
                {sort},
                {expr}
                {vector_aggs}
            FROM
            (
                SELECT
                    {initial_projection},
                    arraySort(x -> x.1, groupArray(({sort}, {vector_group}))) AS `--#v`
                FROM {initial_from} {where_clause}
                GROUP BY {initial_projection}
            )
            ARRAY JOIN
                {metric_vector_aliases}
            SETTINGS enable_unaligned_array_join = 1""")
        q = query_template.format(
            sort=sort,
            initial_projection=', '.join(itertools.chain([key], cols)),
            initial_from=from_clause,
            where_clause=w,
            vector_group=', '.join(metric_ids),
            vector_cols=(',\n'+' '*8).join([f'`--#v`.{v} AS `__{k}`' for k, v in metric_map.items()]),
            chunk_size=chunk_size,
            metric_vector_aliases=(',\n' + ' '*4).join(metric_vector_aliases),
            vector_aggs=(',\n'+' '*4).join(vector_aggs),
            final_projection=', '.join(itertools.chain([key], cols)),
            expr=(', '.join(expr_cols) + ',' if len(expr_cols) > 0 else ''))
        return q

