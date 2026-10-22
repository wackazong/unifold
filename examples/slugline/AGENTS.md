# AGENTS.md: slugline

<!-- unifold:begin - generated block; run `unifold generate` to refresh -->
## unifold

This repository has a [unifold](https://unifold.md) map. A folder with a `unifold.yaml` is a
unit: the file says what the unit provides and needs, and the unit above connects
needs to providers. Read the map before you change an interface; keep it true after.

- `unifold show PATH`: a unit, its capabilities and needs, and who is on the other side
- `unifold capability PATH NAME`: both ends of one connection, with contracts
- `unifold check`: is the map consistent, and does the code agree (`--fix` rewrites generated files)

| Unit | Path | Summary |
|---|---|---|
| cli | `cli` | The slugline command |
| core | `core` | Makes slugs and defines what a transliteration plug-in must offer |
| unicode | `plugins/unicode` | Transliterates Latin letters with diacritics to ASCII |
<!-- unifold:end -->

## Commands

```sh
cargo test --workspace
```
