# slugify

Contract of `core.slugify`: a function that turns one string into one slug, with or without a plug-in. What a slug is, is in [slug.md](slug.md). Notation: wit.
Sources: the tests of `core`

## Parts

### slugify

Kind: query

```wit
slugify: func(input: string, options: options) -> string;
```

Pre: none.
Result: a slug as [slug.md](slug.md) defines it. Letters and digits of ASCII are kept, in lower case. An apostrophe is dropped. Any other ASCII character ends a word. A character outside ASCII is dropped. Exactly one separator stands between two words, none at the start or the end, also after a cut at `max-len`. The result has at most `max-len` characters. A slug is its own slug.
Errors: none.
Examples:

| Case | Input | Expected |
|---|---|---|
| punctuation ends a word | `slugify("Hello, World!", default)` | `hello-world` |
| several spaces | `slugify("two   words", default)` | `two-words` |
| apostrophe dropped | `slugify("Rock 'n' Roll", default)` | `rock-n-roll` |
| own separator | `slugify("Hello, World!", {separator: "_"})` | `hello_world` |
| cut at the limit | `slugify("Hello, World!", {max-len: 6})` | `hello` |
| diacritics dropped | `slugify("Crème brûlée", default)` | `crme-brle` |
| a slug is its own slug | `slugify("hello-world", default)` | `hello-world` |

### slugify-with

Kind: query

```wit
slugify-with: func(input: string, options: options, plugin: borrow<transliterate>) -> string;
```

Pre: none.
Result: a slug like `slugify`, where every character outside ASCII is first given to the plug-in; its answer goes through the slug rules like typed text, and `none` drops the character.
Errors: none.
Examples:

| Case | Input | Expected |
|---|---|---|
| letters replaced | `slugify-with("Crème brûlée", default, latin)` where latin answers `è`→`e`, `û`→`u`, `é`→`e` | `creme-brulee` |
| one letter becomes two | `slugify-with("Straße", default, latin)` where latin answers `ß`→`ss` | `strasse` |
| plug-in does not know | `slugify-with("naïve", default, latin)` where latin answers `ï`→`none` | `nave` |
| empty answer | `slugify-with("a→b", default, latin)` where latin answers `→`→`""` | `ab` |

### options

Kind: type

```wit
record options { separator: char, max-len: option<u32> }
```

| Field | Meaning |
|---|---|
| separator | one character between words; default `-` |
| max-len | the most characters a slug may have; default none |

## Fake

The real implementation: the function is pure, and its users produce inputs that no table can list.
