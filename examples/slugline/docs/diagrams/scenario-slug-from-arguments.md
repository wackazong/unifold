<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: slug-from-arguments

**slugline** · [README](../../README.md) · [component](component.md)

**The command turns its arguments into one slug with the plug-in**
Source: the README of the command
Expect: `slugline Crème brûlée` prints `creme-brulee` and exits with 0

A unit is named by its path from `slugline`; a capability or need of `slugline` is named bare. Every hop is a call along one connection of the map.

```mermaid
sequenceDiagram
  participant pslugline_dcommand as slugline-command
  participant pcli as cli
  participant pcore as core
  participant pplugins__unicode as plugins/unicode
  pslugline_dcommand->>pcli: 1 · slugline
  pcli->>pcore: 2 · slugify-with
  pcli->>pplugins__unicode: 3 · transliterate
  pplugins__unicode->>pcore: 4 · transliterate
  Note over pslugline_dcommand,pplugins__unicode: Expect: `slugline Crème brûlée` prints `creme-brulee` and exits with 0
```

| # | Caller | Target | Part | Contract |
|---|---|---|---|---|
| 1 | `slugline-command` | `cli` | `slugline` | [slugline-command](../references/slugline-command.md) |
| 2 | `cli` | `core` | `slugify-with` | [slugify](../references/slugify.md) |
| 3 | `cli` | `plugins/unicode` | `transliterate` | [transliteration](../references/transliteration.md) |
| 4 | `plugins/unicode` | `core` | `transliterate` | [plugin-api](../references/plugin-api.md) |
