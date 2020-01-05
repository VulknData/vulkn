# Strings

String types are used to represent any non-numeric data

```python
>>> v.select(String('ClickHouse rocks!').alias('string_value')).s

  row  string_value
-----  -----------------
    1  ClickHouse rocks!

(1 row)
```

## ClickHouse references

* [Strings](https://clickhouse.yandex/docs/en/query_language/functions/string_functions/)
* [Searching Strings](https://clickhouse.yandex/docs/en/query_language/functions/string_search_functions/)
* [Replacing Strings](https://clickhouse.yandex/docs/en/query_language/functions/string_replace_functions/)
* [Splitting / merging Strings](https://clickhouse.yandex/docs/en/query_language/functions/splitting_merging_functions/)

---

## Operators

The Vulkn String object supports all common operators. Operators are valid between both Python, Vulkn
and ClickHouse SQL types.

* equals, ```==```, ```v.select(String('ClickHouse') < 'clickhouse').s```
* not equals, ```!=```, ```v.select(String('ClickHouse') != 'clickhouse').s```
* greater than, ```>```, ```v.select(String('ClickHouse') > 'clickhouse').s```
* less than, ```<```, ```v.select(String('ClickHouse') < 'clickhouse').s```
* greater than or equal to, ```>=```, ```v.select(String('ClickHouse') >= 'clickhouse').s```
* less than or equal to, ```<=```, ```v.select(String('ClickHouse') <= 'clickhouse').s```
* concatentation, ```+```, ```v.select(String('ClickHouse') + ' ' + 'clickhouse').s```
* or, ```or```, ```v.select(String('ClickHouse') or 'clickhouse').s```
* by index, ```[idx]```, ```v.select(String('ClickHouse')[1]).s```
* slicing, ```[start:end]```, ```v.select(String('ClickHouse')[1:5]).s```

---

## Functions

### alphaTokens

Return a base64 encoded version of the string.

```python
v.select(String('freedom is the right of all sentient beings').alphaTokens()).s

  row  alphaTokens(\'freedom is the right of all sentient beings\')
-----  --------------------------------------------------------------
    1  ['freedom','is','the','right','of','all','sentient','beings']

(1 row)
```

### appendTrailingCharIfAbsent(char_arg: str), append_if_missing

Return a base64 encoded version of the string.

```python
v.select(String('http://google.com').appendTrailingCharIfAbsent('/')).s
  row  appendTrailingCharIfAbsent(\'http://google.com\', \'/\')
-----  ----------------------------------------------------------
    1  http://google.com/

(1 row)
```

### base64Decode

Return a base64 encoded version of the string.

```python
v.select(String('Q2xpY2tIb3VzZSByb2NrcyE=').base64Decode()).s

  row  base64Decode(\'Q2xpY2tIb3VzZSByb2NrcyE=\')
-----  --------------------------------------------
    1  ClickHouse rocks!

(1 row)
```

### base64Encode

Return a base64 encoded version of the string.

```python
v.select(String('ClickHouse rocks!').base64Encode()).s

  row  base64Encode(\'ClickHouse rocks!\')
-----  -------------------------------------
    1  Q2xpY2tIb3VzZSByb2NrcyE=

(1 row)
```

### len, length, lengthUTF8, character_length, CHARACTER_LENGTH, char_length, CHAR_LENGTH

Return the length of the string. lengthUTF8 returns the UTF8 length of the string.

```python
v.select(String('ClickHouse rocks!').len()).s

  row    length(\'ClickHouse rocks!\')
-----  -------------------------------
    1                               17

(1 row)
```

### concatAssumeInjective(*args)

Same as ```concat```, the difference is that you need to ensure that ```concat(s1, s2, s3) -> s4``` 
is injective, it will be used for optimization of GROUP BY.

### concat(*args)

Concatenates multiple strings.

Concat can be used against both ClickHouse and Python strings:

```python
>>> v.select(String('hello').concat(String(' world')).concat('!')).s

  row  concat(concat(\'hello\', \' world\'), \'!\')
-----  ----------------------------------------------
    1  hello world!

(1 row)
```

Multiple strings can be specified per ```concat``` call:

```python
>>> v.select(String('hello').concat(String(' world'), '!')).s

  row  concat(\'hello\', \' world\', \'!\')
-----  --------------------------------------
    1  hello world!

(1 row)
```

The Python '+' operator can be used in place of the ```concat``` function call:

```python
>>> v.select(String('hello') + String(' world') + '!').s

  row  concat(concat(\'hello\', \' world\'), \'!\')
-----  ----------------------------------------------
    1  hello world!

(1 row)
```

### convertCharset(from_arg: str, to_arg: str)

Converts the string from encoding ```from_arg``` to encoding ```to_arg```.

### CRC32

Returns the CRC32 checksum of a string, using CRC-32-IEEE 802.3 polynomial and initial value 
0xffffffff (zlib implementation).

The result type is UInt32.

```python
>>> v.select(String('hello').CRC32()).s

  row    CRC32(\'hello\')
-----  ------------------
    1           907060870

(1 row)
```

### empty

Returns a boolean 1/true, 0/false value indicating if the string is an empty string.

```python
>>> v.select(String('').empty()).s

  row    empty(\'\')
-----  -------------
    1              1

(1 row)
```

### endswith(pattern: str)

Returns a boolean (1 for true, 0 for false) indicating if the target string ends with the specified
string.

```python
>>> v.select(String('Hello World!').endswith('Hello')).s

  row    like(\'Hello World!\', \'%Hello')
-----  ------------------------------------
    1                                     0

(1 row)
```

### extractAll(pattern: str)

Extracts all instances of the string that match the specified regular expression.

```python
>>> v.select(String('the cat sat').extractAll('.at')).s

  row  extractAll(\'the cat sat\', \'.at\')
-----  --------------------------------------
    1  ['cat','sat']

(1 row)
```

### extract(pattern: str)

Extracts the first instance of the string that matches ```pattern```.

```python
>>> v.select(String('the cat sat').extract('.at')).s

  row  extract(\'the cat sat\', \'.at\')
-----  -----------------------------------
    1  cat

(1 row)
```

### isdecimal

Returns boolean true (1) if the value is a decimal value, boolean false (0) otherwise.

```
>>> v.select(String('1.2').isdecimal()).s

  row    match(\'1.2\', \'^[0-9]*.[0-9]*$\')
-----  -------------------------------------
    1                                      1

(1 row)
```

### isnumeric

Returns boolean true (1) if the value is a numeric value, boolean false (0) otherwise.

```python
>>> v.select(String('1.2').isnumeric()).s

  row    match(\'1.2\', \'^[0-9]*$\')
-----  ------------------------------
    1                               0

(1 row)

>>> v.select(String('1').isnumeric()).s

  row    match(\'1\', \'^[0-9]*$\')
-----  ----------------------------
    1                             1

(1 row)
```

### isValidUTF8

Returns 1, if the set of bytes is valid UTF-8 encoded, otherwise 0.

### join(join_chars: str)

Concatenates/joins the given String array by the specified ```join_chars``` characters.

```python
>>> v.select(String('hello world').split(' '), String('hello world').split(' ').join('|')).s

  row  splitByString(\' \', \'hello world\')    arrayStringConcat(splitByString(\' \', \'hello world\'), \'|\')
-----  ---------------------------------------  -----------------------------------------------------------------
    1  ['hello','world']                        hello|world

(1 row)
```

Python lists can also be joined by declaring the list as an ```Array``` type.

```
>>> v.select(Array(['hello','world']).join('|')).s

  row  arrayStringConcat([\'hello\', \'world\'], \'|\')
-----  --------------------------------------------------
    1  hello|world

(1 row)
```

### like(pattern: str)

Returns boolean true (1) if the string is a simple match for the ```pattern```.

```python
>>> v.select(String('the cat sat').like('%cat%')).s

  row    like(\'the cat sat\', \'%cat%\')
-----  ----------------------------------
    1                                   1

(1 row)
```

### lower, lowerUTF8, lcase

Converts the string to lowercase.

```
>>> v.select(String('HELLO WOrlD').lower()).s

  row  lower(\'HELLO WOrlD\')
-----  ------------------------
    1  hello world

(1 row)
```

### match(pattern: str)

Returns boolean true (1) if the regular expression ```pattern``` can be found within the specified string.

```python
>>> v.select(String('the cat sat').match('.at')).s

  row    match(\'the cat sat\', \'.at\')
-----  ---------------------------------
    1                                  1

(1 row)
```

### notEmpty

Returns a boolean 1/true, 0/false value indicating if the string is not an empty string.

```python
>>> v.select(String('').notEmpty()).s

  row    notEmpty(\'\')
-----  ----------------
    1                 0

(1 row)
```

### notLike(pattern: str)

Returns a boolean 1/true, 0/false value indicating if the string doesn't match the specified search string.

```python
>>> v.select(String('Hello World! World!').notLike('%World%')).s

  row    notLike(\'Hello World! World!\', \'%World%\')
-----  -----------------------------------------------
    1                                                0

(1 row)
```

### positionCaseInsensitive(needle: str), positionCaseInsensitiveUTF8

Returns the starting position of the first instance of the case insensitive specified string.

```python
>>> v.select(String('Hello World! World!').positionCaseInsensitive('world')).s

  row    positionCaseInsensitive(\'Hello World! World!\', \'world\')
-----  -------------------------------------------------------------
    1                                                              7

(1 row)
```

### position(needle: str), positionUTF8

Returns the starting position of the first instance of the specified string.

```python
>>> v.select(String('Hello World! World!').position('World')).s

  row    position(\'Hello World! World!\', \'World\')
-----  ----------------------------------------------
    1                                               7

(1 row)
```

### replaceAll(pattern, replacement)

Replace all found instances of the specified string.

```
>>> v.select(String('Hello World! World!').replaceAll('World', 'foobar')).s

  row  replaceAll(\'Hello World! World!\', \'World\', \'foobar\')
-----  ------------------------------------------------------------
    1  Hello foobar! foobar!

(1 row)
```

### replaceOne(pattern, replacement)

Replace the first found instance of the specified string.

```python
>>> v.select(String('Hello World! World!').replaceOne('World', 'foobar')).s

  row  replaceOne(\'Hello World! World!\', \'World\', \'foobar\')
-----  ------------------------------------------------------------
    1  Hello foobar! World!

(1 row)
```

### replaceRegexpAll(pattern, replacement)

Replace all found instances that match the regular expression.

```python
>>> v.select(String('Hello World! World!').replaceRegexpAll('World(!|$)', 'foobar')).s

  row  replaceRegexpAll(\'Hello World! World!\', \'World(!|$)\', \'foobar\')
-----  -----------------------------------------------------------------------
    1  Hello foobar foobar

(1 row)
```

### replaceRegexpOne(pattern, replacement)

Replace the first found instance matching the regular expression.

```python
>>> v.select(String('Hello World! World!').replaceRegexpOne('! World.*$', 'foobar')).s

  row  replaceRegexpOne(\'Hello World! World!\', \'! World.*$\', \'foobar\')
-----  -----------------------------------------------------------------------
    1  Hello Worldfoobar

(1 row)
```

### replace(pattern, replacement, count=None)

Replace the specified portion of the string.

```python
>>> v.select(String('Hello World!').replace('World', 'foobar')).s

  row  replaceAll(\'Hello World!\', \'World\', \'foobar\')
-----  -----------------------------------------------------
    1  Hello foobar!

(1 row)
```

### reverse, reverseUTF8

Reverse the given string.

```python
>>> v.select(String('Hello World!').reverse()).s

  row  reverse(\'Hello World!\')
-----  ---------------------------
    1  !dlroW olleH

(1 row)
```

### split(separator: str), splitByString(separator: str), splitByChar(separator_arg: str)

Splits the string into an array using the separator character. splitByChar only accepts a single
character argument.

```python
v.select(String('freedom is the right of all sentient beings').split(' ')).s 

  row  splitByString(\' \', \'freedom is the right of all sentient beings\')
-----  -----------------------------------------------------------------------
    1  ['freedom','is','the','right','of','all','sentient','beings']

(1 row)
```

### splitlines

Splits the string into an array using the '\n' newline character as the separator.v.select(String('Hello\\nworld!').splitlines()).s

```python
>>> v.select(String('Hello\nWorld!').splitlines()).s

  row  splitByChar(\'\\n\', \'Hello\\nWorld!\')
-----  ------------------------------------------
    1  ['Hello','World!']

(1 row)
```

### startswith(pattern: str)

Returns a boolean (1 for true, 0 for false) indicated if the target string starts with the specific string.

```python
>>> v.select(String('Hello World!').startswith('Hello')).s

  row    like(\'Hello World!\', \'Hello%\')
-----  ------------------------------------
    1                                     1

(1 row)
```

### substring(offset, length=None), substringUTF8(offset, length=None)

Returns the substring of the target string starting from ```offset``` with length ```length```.

```python
>>> v.select(String('Hello World!').substring(2, 3)).s

  row  substring(\'Hello World!\', 2, 3)
-----  -----------------------------------
    1  ell

(1 row)
```

### toValidUTF8

Converts the specified string to UTF8.

```python
>>> v.select(String('Hello World!').toValidUTF8()).s

  row  toValidUTF8(\'Hello World!\')
-----  -------------------------------
    1  Hello World!

(1 row)
```

### trimBoth

Trims empty white space from both sides of a string.

```python
>>> v.select(String('  Hello World!  ').trimBoth()).s

  row  trimBoth(\'  Hello World!  \')
-----  --------------------------------
    1  Hello World!

(1 row)
```

### trimLeft(trim_str: str='\\\\\s*'), ltrim, lstrip

Trims the specified regex/character from the left side of a string. Any white space character by default.

```python
>>> v.select(String('  Hello World!').trimLeft()).s

  row  trimLeft(\'  Hello World!\')
-----  ------------------------------
    1  Hello World!

(1 row)
```

### trimRight(trim_str: str='\\\\\s*'), rtrim, rstrip

Trims the specified regex/character from the right side of a string. Any white space character by default.

```python
>>> v.with_(String('Hello World!   ').alias('example')).select(String(n='example').len(), String(n='example').trimRight().len()).s

  row    length(example)    length(trimRight(example))
-----  -----------------  ----------------------------
    1                 15                            12

(1 row)
```

### trim(trim_str: str='\\\\\s*'), strip

Trims the specified regex/character from both sides of a string. Any white space character by default.

```python
>>> v.select(String('  Hello World!   ').strip()).s

  row  replaceRegexpAll(\'  Hello World!   \', \'^\\\\s*|\\\\s*$\', \'\')
-----  --------------------------------------------------------------------
    1  Hello World!

(1 row)
```

### tryBase64Decode

Attempt to base64 decode the specified string

```python
>>> v.select(String('Hello World!').base64Encode().tryBase64Decode()).s

  row  tryBase64Decode(base64Encode(\'Hello World!\'))
-----  ------------------------------------------------------
    1  Hello World!

(1 row)
```

### upper, ucase, upperUTF8

Converts the string to uppercase.

```python
v.select(String('hello world').ucase()).s

  row  ucase(\'hello world\')
-----  ------------------------
    1  HELLO WORLD

(1 row)
```

### unhex

Applies the unhex operation to a string previously encoded into hex.

```python
>>> v.select(funcs.encode.hex('HelloWorld').unhex()).s

  row  unhex(hex(\'HelloWorld\'))
-----  ----------------------------
    1  HelloWorld

(1 row)
```