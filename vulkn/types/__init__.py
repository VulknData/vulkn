# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from vulkn.types.string import String
from vulkn.types.url import URL
from vulkn.types.array import Array
from vulkn.types.base import TypeBase, Literal
from vulkn.types.numeric import Numeric
from vulkn.types.integer import UInt8, UInt16, UInt32, UInt64, Int8, Int16, Int32, Int64
from vulkn.types.float import Float, Float32, Float64
from vulkn.types.boolean import Boolean
from vulkn.types.date import Date, DateTime
from vulkn.types.url import URL
from vulkn.types.json import JSON
from vulkn.types.ipaddress import IP
from vulkn.types.array_vector import ArrayVector
from vulkn.types.column_vector import ColumnVector
from vulkn.types.merge_vector import MergeVector
from vulkn.types.column_type import ColumnType
from vulkn.types.uuid import UUID

Vector = ArrayVector

vS = String
vU = URL
vA = Array
vN = Numeric
vU8 = UInt8
vU16 = UInt16
vU32 = UInt32
vU64 = UInt64
vI8 = Int8
vI16 = Int16
vI32 = Int32
vI64 = Int64
vF32 = Float32
vF64 = Float64
vD = Date
vDT = DateTime
vDT32 = DateTime
col = lambda x: TypeBase(Literal(x))
c = col
null = c('NULL')
NULL = null


"""
TODO: Next release.

Strings:
- Add String function format
- Add searching strings https://clickhouse.yandex/docs/en/query_language/functions/string_search_functions/
- Add replacing strings https://clickhouse.yandex/docs/en/query_language/functions/string_replace_functions/
Type Conversion:
- https://clickhouse.yandex/docs/en/query_language/functions/type_conversion_functions/
Dates:
- Add toRelative*, add*, subtract* functions
Arrays
- https://clickhouse.yandex/docs/en/query_language/functions/array_functions/
Hash
- https://clickhouse.yandex/docs/en/query_language/functions/hash_functions/
Dictionaries
- https://clickhouse.yandex/docs/en/query_language/functions/ext_dict_functions/
ML
- https://clickhouse.yandex/docs/en/query_language/functions/machine_learning_functions/
Other
- https://clickhouse.yandex/docs/en/query_language/functions/other_functions/
"""
