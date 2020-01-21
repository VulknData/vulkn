# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


def quote_literal(value: any) -> any:
    if isinstance(value, str):
        return "'{}'".format(value)
    elif is_literal_type(value):
        return value
    else:
        if isinstance(value, list):
            a = []
            for v in value:
                if isinstance(v, str):
                    a.append("'{}'".format(str(v).encode('unicode-escape').decode()))
                else:
                    a.append(str(v))
            return '[{}]'.format(', '.join(a))
            #return '[{}]'.format(','.join(["'{}'".format(str(v).encode('unicode-escape').decode()) for v in value]))
            #return '[{}]'.format(','.join(["{}".format(str(v).encode('unicode-escape').decode()) for v in value]))
        else:
            return str(value)


format_python_type = quote_literal


class ColumnBaseMixIn:
    def alias(self, alias: str) -> any:
        r = type(self)(FunctionExpression('alias', str(self), alias))
        return r

    as_ = alias

    def cast(self, type_arg: str) -> any:
        from vulkn.types.string import String
        from vulkn.types.array import Array
        from vulkn.types.boolean import Boolean
        from vulkn.types.integer import Int8, Int16, Int32, Int64
        from vulkn.types.integer import UInt8, UInt16, UInt32, UInt64
        from vulkn.types.date import Date, DateTime
                
        k = getattr(type_arg, 'CAST', type_arg)
        return locals()[k](FunctionExpression('cast', Literal(str(self)), k))


class Literal(ColumnBaseMixIn):
    def __init__(self, value: any) -> None:
        self._value = value

    def __str__(self) -> str:
        if self._value is None:
            return 'NULL'
        else:
            return str(self._value)


Expression = Literal


class FunctionExpression:
    def __init__(self, el: str, *args: list) -> None:
        self._el = el
        self._args = args

    def __str__(self) -> str:
        if self._el == 'alias':
            return '{} AS `{}`'.format(str(self._args[0]), self._args[1])
        else:
            args = ["'{}'".format(a) if isinstance(a, str) else str(a) for a in self._args]
            return '{}({})'.format(self._el, ','.join(map(str, args)))


func = FunctionExpression


def is_literal_type(t) -> bool:
    return (isinstance(t, Literal) or 
            isinstance(t, Expression) or 
            isinstance(t, FunctionExpression))


class TypeBase(ColumnBaseMixIn):
    _METHODS = {}
    TYPE = 'String'
    CAST = TYPE

    def __init__(self, value: any=None, name: str=None, n: str=None) -> None:
        self._value = Literal('"{}"'.format(name or n)) if (name or n) else value

    def __str__(self) -> str:
        return (str(self._value) if is_literal_type(self._value) 
                else format_python_type(self._value))

    @property
    def sql(self):
        return str(self)

    @property
    def methods(self) -> dict:
        r = {}
        if 'methods' in dir(super()):
            r.update(super().methods)
        r.update(self._METHODS)
        return r

    def __getattr__(self, name: str) -> any:
        def _method():
            from vulkn.types.string import String
            from vulkn.types.array import Array
            from vulkn.types.boolean import Boolean
            from vulkn.types.integer import Int8, Int16, Int32, Int64
            from vulkn.types.integer import UInt8, UInt16, UInt32, UInt64
            from vulkn.types.date import Date, DateTime

            rtype = (locals()[self.methods[name]] 
                if self.methods[name] is not None
                else type(self))
            
            return rtype(FunctionExpression(name, self._value))

        if name in self.methods:
            return _method
        else:
            raise AttributeError
 
    def _in(self, operator, right):
        from vulkn.types.integer import UInt8
        from vulkn.datatable import VulknDataTable
        in_arg = None
        if hasattr(right, 'show_sql'):
            in_arg = right.show_sql()[0:-1]
        elif isinstance(right, list):
            if isinstance(right[0], str):
                in_arg = "'{}'".format("','".join(map(str, right)))
            else:
                in_arg = ','.join(map(str, right))
        else:
            in_arg = str(right)
        return UInt8(Literal('{} {} ({})'.format(self._value, operator, in_arg)))

    def In(self, right):
        return self._in('IN', right)

    in_ = In

    def notIn(self, right):
        return self._in('NOT IN', right)

    not_in = notIn
    not_in_ = notIn

    def globalIn(self, right):
        return self._in('GLOBAL IN', right)

    global_in = globalIn
    global_in_ = globalIn

    def globalNotIn(self, right):
        return self._in('GLOBAL NOT IN', right)

    global_not_in = globalNotIn
    global_not_in_ = globalNotIn

    def isNull(self):
        from vulkn.types.integer import UInt8
        return UInt8(func('isNull', self._value))

    is_null = isNull
    isn = isNull

    def isNotNull(self):
        from vulkn.types.integer import UInt8
        return UInt8(func('isNotNull', self._value))

    is_not_null = isNotNull
    isnn = isNotNull

    def ifNull(self, other):
        return Literal(func('ifNull', self._value, other))

    if_null = ifNull

    def nullIf(self, test):
        return Literal(func('nullIf', self._value, test))

    null_if = nullIf

    def assumeNotNull(self):
        return type(self)(func('assumeNotNull', self._value))

    assume_not_null = assumeNotNull
    nn = assumeNotNull

    def toNullable(self):
        return type(self)(func('toNullable', self._value))

    to_nullable = toNullable
    tn = toNullable

    def between(self, start, end):
        from vulkn.types.integer import UInt8
        return UInt8(Literal('{} BETWEEN {} AND {}'.format(self._value, start, end)))

    bt = between

    def notBetween(self, start, end):
        from vulkn.types.integer import UInt8
        return UInt8(Literal('{} NOT BETWEEN {} AND {}'.format(self._value, start, end)))

    not_between = notBetween
    nbt = notBetween

    def typename(self):
        from vulkn.types.string import String
        return String(Literal(f'toTypeName({self._value})'))

    def __eq__(self, right) -> any:
        from vulkn.types.integer import UInt8
        return UInt8(func('equals', self._value, right))

    eq = __eq__
    equals = __eq__
        
    def __ne__(self, right) -> any:
        from vulkn.types.integer import UInt8
        return UInt8(func('notEquals', self._value, right))

    ne = __ne__
    notEquals = __ne__
    not_equals = __ne__

    def __gt__(self, right) -> any:
        from vulkn.types.integer import UInt8
        return UInt8(func('greater', self._value, right))

    gt = __gt__
    greater = __gt__
        
    def __lt__(self, right) -> any:
        from vulkn.types.integer import UInt8
        return UInt8(func('less', self._value, right))

    lt = __lt__
    less = __lt__

    def __ge__(self, right) -> any:
        from vulkn.types.integer import UInt8
        return UInt8(func('greaterOrEquals', self._value, right))
        
    ge = __ge__
    greaterOrEquals = __ge__
    greater_or_equals = __ge__

    def __le__(self, right) -> any:
        from vulkn.types.integer import UInt8
        return UInt8(func('lessOrEquals', self._value, right))

    le = __le__
    lessOrEquals = __le__
    less_or_equals = __le__

    def and_(self, right) -> any:
        from vulkn.types.integer import UInt8
        return UInt8(func('and', self._value, right))

    def __and__(self, right) -> any:
        from vulkn.types.integer import UInt8
        return UInt8(func('bitAnd', self._value, right))

    bitAnd = __and__
    bit_and = __and__

    def or_(self, right) -> any:
        from vulkn.types.integer import UInt8
        return UInt8(func('or', self._value, right))

    def __or__(self, right) -> any:
        from vulkn.types.integer import UInt8
        return UInt8(func('bitOr', self._value, right))

    bitOr = __or__
    bit_or = __or__
        
    def not_(self) -> any:
        from vulkn.types.integer import UInt8
        return UInt8(func('not', self._value))

    def __invert__(self) -> any:
        from vulkn.types.integer import UInt8
        return UInt8(func('bitNot', self._value))

    bitNot = __invert__
    bit_not = __invert__

    def __xor__(self, right) -> any:
        from vulkn.types.integer import UInt8
        return UInt8(func('xor', self._value, right))

    xor = __xor__
    xor_ = __xor__
    bitXor = __xor__
    bit_xor = __xor__
