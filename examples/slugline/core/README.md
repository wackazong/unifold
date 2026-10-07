# core

`core` turns a string into a URL slug and defines the interface through which
other code can teach it to transliterate.

## Provides

### `slugify`

`slugify("Hello World")` returns `hello-world`.

- The result contains only `a-z`, `0-9` and the separator.
- The result is at most `max_len` bytes long and never ends with the
  separator.
- The same input and options always give the same result.
- Characters outside ASCII are dropped unless a transliterator is given.

### `plugin-api`

The trait `Transliterator`: one function that maps a character to an ASCII
string, possibly empty. An implementation must be free of side effects and
must return the same answer for the same character.
