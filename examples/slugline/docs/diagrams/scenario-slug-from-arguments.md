<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: slug-from-arguments

**slugline** · [README](../../README.md) · [component](component.md)

**The command turns its arguments into one slug with the plug-in**
Source: the README of the command
Expect: `slugline Crème brûlée` prints `creme-brulee` and exits with 0

A unit is named by its path from `slugline`; a capability or need of `slugline` is named bare. Every step is one hop along one connection of the map, drawn as the kind of its part says: a command or query goes from the caller to the target, and a dashed arrow brings the result of a query back; an event goes from the provider that raises it to the caller that receives it, with an open arrowhead. A bar is the time a lifeline is busy with a step; it ends when a lifeline further out makes the next step, and a unit below the busy one acts for it. An event from an idle lifeline lands on the bar of a busy receiver, or starts one.

```mermaid
---
config:
  sequence:
    height: 108
---
sequenceDiagram
  participant pslugline_dcommand as slugline-command<br/>«cli»<br/>Slugs from arguments or from the<br/>lines of standard input
  participant pcli as cli<br/>«adapter»<br/>The slugline command
  participant pcore as core<br/>«logic»<br/>Makes slugs and defines what a<br/>transliteration plug-in must<br/>provide
  participant pplugins__unicode as plugins/unicode<br/>«logic»<br/>Transliterates Latin letters<br/>with diacritics to ASCII
  pslugline_dcommand->>pcli: 1 · slugline
  activate pcli
  pcli->>pcore: 2 · slugify-with
  activate pcore
  pcore-->>pcli: ↩ 2
  deactivate pcore
  pcli->>pplugins__unicode: 3 · transliterate
  activate pplugins__unicode
  pplugins__unicode->>pcore: 4 · transliterate
  pplugins__unicode-->>pcli: ↩ 3
  deactivate pplugins__unicode
  deactivate pcli
  Note over pslugline_dcommand,pplugins__unicode: wrap: Expect: `slugline Crème brûlée` prints `creme-brulee` and exits with 0
```

| # | Caller | Target | Part | Kind | Contract |
|---|---|---|---|---|---|
| 1 | `slugline-command` | `cli` | `slugline` | command | [slugline-command](../references/slugline-command.md) |
| 2 | `cli` | `core` | `slugify-with` | query | [slugify](../references/slugify.md) |
| 3 | `cli` | `plugins/unicode` | `transliterate` | query | [transliteration](../references/transliteration.md) |
| 4 | `plugins/unicode` | `core` | `transliterate` | type | [plugin-api](../references/plugin-api.md) |
