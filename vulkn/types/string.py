# -*- coding: utf-8 -*-

# Copyright (c) 2019, Jason Godden <jason@godden.id.au>
# Copyright (c) 2019, VulknData Pty Ltd
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-only


from vulkn.types.base import TypeBase, func
from vulkn.types.array import Array
from vulkn.types.integer import UInt8, UInt32, UInt64
from vulkn.utils import item_index


class String(TypeBase):
    TYPE = 'String'
    CAST = 'String'
    _METHODS = {
        'alphaTokens': 'Array',
        'empty': 'UInt8',
        'notEmpty': 'UInt8',
        'length': 'UInt64',
        'lengthUTF8': 'UInt64',
        'char_length': 'UInt64',
        'CHAR_LENGTH': 'UInt64',
        'character_length': 'UInt64',
        'CHARACTER_LENGTH': 'UInt64',
        'lower': None,
        'lcase': None,
        'upper': None,
        'ucase': None,
        'lowerUTF8': None,
        'upperUTF8': None,
        'isValidUTF8': 'UInt8',
        'toValidUTF8': None,
        'reverse': None,
        'reverseUTF8': None,
        'base64Encode': None,
        'base64Decode': None,
        'tryBase64Decode': None,
        'unhex': None,
        'trimLeft': None,
        'trimRight': None,
        'trimBoth': None,
        'CRC32': 'UInt32',
        'CRC64': 'UInt64',
        'CRC32IEEE': 'UInt32',
        'MD5': None,
        'SHA1': None,
        'SHA224': None,
        'SHA256': None,
        'basename': None
    }

    def __add__(self, right):
        return self.concat(right)

    def __getitem__(self, index):
        start, stop = item_index(index)
        if stop is None:
            stop = 1
        return String(func('substring', self._value, start, stop))
        
    def substring(self, offset, length=None):
        if length:
            return String(func('substring', self._value, offset, length))
        return String(func('substring', self._value, offset))

    mid = substring
    substr = substring

    def len(self):
        return UInt64(func('length', self._value))

    def substringUTF8(self, offset, length=None):
        if length:
            return String(func('substringUTF8', self._value, offset, length))
        return String(func('substringUTF8', self._value, offset))

    def trim(self, trim_str: str='\\\s*'):
        return self.replaceRegexpAll('^{}|{}$'.format(trim_str, trim_str), '')

    strip = trim
        
    def isnumeric(self):
        return self.match('^[0-9]*$')

    def isdecimal(self):
        return self.match('^[0-9]*\.[0-9]*$')

    def ltrim(self, trim_str: str='\\\s*'):
        return self.replaceRegexpOne('^{}'.format(trim_str), '')

    lstrip = ltrim
        
    def rtrim(self, trim_str: str='\\\s*'):
        return self.replaceRegexpOne('{}$'.format(trim_str), '')

    rstrip = rtrim
            
    def position(self, needle: str):
        return String(func('position', self._value, needle))

    locate = position

    def positionUTF8(self, needle: str):
        return String(func('positionUTF8', self._value, needle)) 

    def positionCaseInsensitive(self, needle: str):
        return String(func('positionCaseInsensitive', self._value, needle))

    def positionCaseInsensitiveUTF8(self, needle: str):
        return String(func('positionCaseInsensitiveUTF8', self._value, needle))

    def replaceOne(self, pattern, replacement):
        return String(func('replaceOne', self._value, pattern, replacement))

    def replaceAll(self, pattern, replacement):
        return String(func('replaceAll', self._value, pattern, replacement))

    def replaceRegexpOne(self, pattern, replacement):
        return String(func('replaceRegexpOne', self._value, pattern, replacement))

    def replaceRegexpAll(self, pattern, replacement):
        return String(func('replaceRegexpAll', self._value, pattern, replacement))

    def replace(self, pattern, replacement, count=None):
        if count:
            return self.replaceOne(pattern, replacement)
        else:
            return self.replaceAll(pattern, replacement)

    def match(self, pattern: str):
        return String(func('match', self._value, pattern))

    def extract(self, pattern: str):
        return String(func('extract', self._value, pattern))

    def extractAll(self, pattern: str):
        return String(func('extractAll', self._value, pattern))

    def like(self, pattern: str):
        return UInt8(func('like', self._value, pattern))

    def notLike(self, pattern: str):
        return String(func('notLike', self._value, pattern))

    def splitByString(self, separator_arg: str) -> Array:
        return Array(func('splitByString', separator_arg, self._value))

    def splitByChar(self, separator_arg: str) -> Array:
        return Array(func('splitByChar', separator_arg, self._value))

    def concat(self, *args):
        return String(func('concat', *([self._value] + [*args])))

    def concatAssumeInjective(self, *args):
        return String(func('concatAssumeInjective', *([self._value] + [*args])))
        
    def appendTrailingCharIfAbsent(self, char_arg: str):
        return String(
            func('appendTrailingCharIfAbsent', self._value, char_arg))

    append_if_missing = appendTrailingCharIfAbsent

    def convertCharset(self, from_arg: str, to_arg: str):
        return String(func('convertCharset', self._value, from_arg, to_arg))

    def splitlines(self) -> Array:
        return self.splitByChar('\\n')

    def startswith(self, pattern: str):
        return self.like('{}%'.format(pattern))
    
    def endswith(self, pattern: str):
        return self.like('%{}'.format(pattern))

    split = splitByString

    def join(self, arr):
        return String(func('arrayStringConcat', self._value, arr))
