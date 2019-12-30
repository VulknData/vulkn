# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from vulkn.types.base import func, TypeBase, Literal
from vulkn.types import UInt16, UInt8, UInt32


class DateTimeBase(TypeBase):
    _METHODS = {
        'toTimeZone': None
    }

    @staticmethod
    def _with_timezone(*args, timezone):
        return (*args, Literal("'{}'".format(timezone))) if timezone else args

    def toStartOfInterval(self, interval, timezone=None):
        return type(self)(func('toStartOfInterval',
                               *DateTimeBase._with_timezone(self,
                                                            Literal('INTERVAL ' + interval),
                                                            timezone=timezone)))

    time_bucket = toStartOfInterval

    def toStartOfWeek(self, mode=0):
        return Date(func('toStartOfWeek', self, mode))

    def toYearWeek(self, mode=0, timezone=None):
        return type(self)(func('toYearWeek', *DateTimeBase._with_timezone(self, mode, timezone=timezone)))

    def toWeek(self, mode=0, timezone=None):
        return type(self)(func('toWeek', *DateTimeBase._with_timezone(self, mode, timezone=timezone)))

    def toYear(self, timezone=None):
        return UInt16(func('toYear', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toQuarter(self, timezone=None):
        return UInt8(func('toQuarter', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toMonth(self, timezone=None):
        return UInt8(func('toMonth', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toDayOfYear(self, timezone=None):
        return UInt16(func('toDayOfYear', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toDayOfMonth(self, timezone=None):
        return UInt8(func('toDayOfMonth', *DateTimeBase._with_timezone(self, timezone=timezone)))
        
    def toDayOfWeek(self, timezone=None):
        return UInt8(func('toDayOfWeek', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toStartOfMonth(self, timezone=None):
        return type(self)(func('toStartOfMonth', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toStartOfQuarter(self, timezone=None):
        return type(self)(func('toStartOfQuarter', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toStartOfYear(self, timezone=None):
        return type(self)(func('toStartOfYear', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toStartOfISOYear(self, timezone=None):
        return type(self)(func('toStartOfISOYear', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def formatDateTime(self, formatstr, timezone):
        return String(func('toStartOfISOYear', *DateTimeBase._with_timezone(self, formatstr, timezone=timezone)))

    def dateDiff(self, unit, other, timezone=None):
        return type(self)(func('dateDiff', *DateTimeBase._with_timezone(unit, self, other, timezone=timezone)))

    def toYYYYMM(self, timezone=None):
        return type(self)(func('toYYYYMM', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toYYYYMMDD(self, timezone=None):
        return type(self)(func('toYYYYMMDD', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toYYYYMMDDhhmmss(self, timezone=None):
        return type(self)(func('toYYYYMMDDhhmmss', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toISOWeek(self, timezone=None):
        return type(self)(func('toISOWeek', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toISOYear(self, timezone=None):
        return type(self)(func('toISOYear', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toMonday(self, timezone=None):
        return Date(func('toMonday', self))


class Date(DateTimeBase):
    TYPE = 'Date'
    CAST = 'Date'

    def __str__(self) -> str:
        if type(self._value) is Literal:
            return str(self._value)
        if type(self._value) is func:
            return str(self._value)
        return str("toDate('{}')".format(self._value))

    @classmethod
    def yesterday(self):
        return Date(Literal('yesterday()'))

    @classmethod
    def today(self):
        return Date(Literal('today()'))


class DateTime(DateTimeBase):
    TYPE = 'DateTime'
    CAST = 'DateTime'

    def __str__(self) -> str:
        if type(self._value) is Literal:
            return str(self._value)
        if type(self._value) is func:
            return str(self._value)
        return str("toDateTime('{}')".format(self._value))

    @classmethod
    def now(self):
        return DateTime(Literal('now()'))

    @staticmethod
    def timeSlots(start_time, duration, size):
        return DateTime(func('timeSlots', self, duration, size))

    def toStartOfYear(self, timezone=None):
        return Date(func('toStartOfYear', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toStartOfQuarter(self, timezone=None):
        return Date(func('toStartOfQuarter', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toStartOfMonth(self, timezone=None):
        return Date(func('toStartOfMonth', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toStartOfWeek(self, mode=0, timezone=None):
        return Date(func('toStartOfWeek', *DateTimeBase._with_timezone(self, mode, timezone=timezone)))

    def toStartOfDay(self, timezone=None):
        return DateTime(func('toStartOfDay', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toStartOfHour(self, timezone=None):
        return DateTime(func('toStartOfHour', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toStartOfFifteenMinutes(self, timezone=None):
        return DateTime(func('toStartOfFifteenMinutes', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toStartOfTenMinutes(self, timezone=None):
        return DateTime(func('toStartOfTenMinutes', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toStartOfFiveMinute(self, timezone=None):
        return DateTime(func('toStartOfFiveMinute', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toStartOfMinute(self, timezone=None):
        return DateTime(func('toStartOfMinute', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toUnixTimestamp(self, timezone=None):
        return UInt32(func('toUnixTimestamp', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def timeSlot(self, timezone=None):
        return DateTime(func('timeSlot', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toTime(self, timezone=None):
        return DateTime(func('toTime', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toHour(self, timezone=None):
        return UInt8(func('toHour', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toMinute(self, timezone=None):
        return UInt8(func('toMinute', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toSecond(self, timezone=None):
        return UInt8(func('toSecond', *DateTimeBase._with_timezone(self, timezone=timezone)))

    def toMonday(self, timezone=None):
        return Date(func('toMonday', *DateTimeBase._with_timezone(self, timezone=timezone)))