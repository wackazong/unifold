# Three commands

What the reference tool prints for this project. Run them in the root of slugline, with `unifold` as the alias from [README.md](../../README.md).

```console
$ unifold check
4 unit(s): 0 error(s), 0 warning(s), 0 info; 3 dependencies observed in code
```

The three dependencies are read from the `Cargo.toml` files.

```console
$ unifold show plugins/unicode
unit      unicode  (plugins/unicode)
summary   Transliterates Latin letters with diacritics to ASCII
status    active · library
manifest  plugins/unicode/unifold.yaml
parent    slugline
children  none
capabilities
  transliteration (library): Replaces Latin letters that have diacritics, and ligatures, by ASCII letters  contract docs/references/transliteration.md  verified by plugins/unicode/tests/latin.rs
      used by cli as need 'transliteration'
needs
  plugin-api (library): The trait a transliteration plug-in implements  contract docs/references/plugin-api.md
      provided by core capability 'plugin-api'  verified by core/tests/plugin.rs
```

```console
$ unifold capability plugins/unicode plugin-api
--- plugins/unicode needs 'plugin-api' (library): The trait a transliteration plug-in implements
    contract: docs/references/plugin-api.md

--- core capabilities 'plugin-api' (library): The trait a transliteration plug-in implements, and a slugify that uses one
    contract: docs/references/plugin-api.md
    verified by: core/tests/plugin.rs
`slugify_with(input, &options, &plugin)` asks a `Transliterate` plug-in:

- only about characters outside ASCII;
- an answer is treated like typed text, and may have several letters or none;
- `None` drops the character.

Contract: [plugin-api](../docs/references/plugin-api.md). Tests:
[tests/plugin.rs](tests/plugin.rs).
```
