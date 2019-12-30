# Strings

ClickHouse reference - [Strings]()

String types are used to represent any non-numeric data

```python
v.select(String('ClickHouse rocks!').alias('string_value')).s

  row  string_value
-----  -----------------
    1  ClickHouse rocks!

(1 row)
```

---

## Operators

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
### concat(*args)
### convertCharset(from_arg: str, to_arg: str)
### CRC32
### empty
### endswith(pattern: str)
### extractAll(pattern: str)
### extract(pattern: str)
### isdecimal
### isnumeric
### isValidUTF8
### join(arr)
### lcase
### lengthUTF8
### like(pattern: str)
### lower
### lowerUTF8
### ltrim(trim_str: str='//s*')
### match(pattern: str)
### notEmpty
### notLike(pattern: str)
### positionCaseInsensitive(needle: str)
### positionCaseInsensitiveUTF8(needle: str)
### position(needle: str)
### positionUTF8(needle: str)
### replaceAll(pattern, replacement)
### replaceOne(pattern, replacement)
### replaceRegexpAll(pattern, replacement)
### replaceRegexpOne(pattern, replacement)
### replace(pattern, replacement, count=None)
### reverse
### reverseUTF8
### rtrim(trim_str: str=None)
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

  row  splitByChar(\'\\n\', \'Hello\\nworld!\')
-----  ------------------------------------------
    1  ['Hello','world!']

(1 row)
v.select(String('Hello\\nworld!').splitlines()).s

  row  splitByChar(\'\\n\', \'Hello\\nworld!\')
-----  ------------------------------------------
    1  ['Hello','world!']

(1 row)
```python
v.select(String('Hello\\nworld!').splitlines()).s

  row  splitByChar(\'\\n\', \'Hello\\nworld!\')
-----  ------------------------------------------
    1  ['Hello','world!']

(1 row)
```

### startswith(pattern: str)
### substring(offset, length=None)
### substringUTF8(offset, length=None)
### toValidUTF8
### trimBoth
### trimLeft
### trimRight
### trim(trim_str: str='//s*')
### tryBase64Decode
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
