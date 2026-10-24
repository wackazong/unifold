# unicode

A transliteration plug-in: it replaces Latin letters that have diacritics, and ligatures such as `æ`, by ASCII letters, so that a slug of `Crème brûlée` keeps its letters instead of losing them.

## Why

Character tables are large and a matter of taste, so they live outside the library that makes slugs, behind the trait that library defines. This crate is one such table, for Latin script. Another script is another plug-in, not a change here, and a user who wants no transliteration leaves this crate out.

## Out of scope

- Scripts other than Latin: Cyrillic, Greek or CJK need a plug-in of their own.
