# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


import re

import sqlparse
import sqlparse.keywords
from sqlparse.sql import TokenList


class Where(sqlparse.sql.TokenList):
    M_OPEN = sqlparse.tokens.Keyword, 'WHERE'
    M_CLOSE = sqlparse.tokens.Keyword, (
        'ORDER BY', 'GROUP BY', 'VECTORIZE BY', 'LIMIT', 'UNION', 'UNION ALL', 'EXCEPT', 'HAVING', 
        'RETURNING', 'INTO')

sqlparse.sql.Where = Where

SQL_REGEX = {
    'clickhouse-ext': [
        (r'VECTORIZE\s+BY\b', sqlparse.tokens.Keyword),
        (r'CHUNK\s+BY\b', sqlparse.tokens.Keyword)
    ]
}

FLAGS = re.IGNORECASE | re.UNICODE
SQL_REGEX = [(re.compile(rx, FLAGS).match, tt) for rx, tt in SQL_REGEX['clickhouse-ext']]

sqlparse.keywords.SQL_REGEX = SQL_REGEX + sqlparse.keywords.SQL_REGEX
sqlparse.lexer.SQL_REGEX = sqlparse.keywords.SQL_REGEX
