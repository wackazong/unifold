<!-- unifold:generated - do not edit; run `unifold check --fix` -->
# Scenario: library-call

**slugline** · [README](../../README.md) · [component](component.md)

**A program calls the library with a plug-in of its own**
Source: the tests of core
Expect: `slugify_with("Straße", &Options::default(), &plugin)` returns `strasse` when the plug-in answers `ss` for `ß`

A unit is named by its path from `slugline`; a capability or need of `slugline` is named bare. Every step is one hop along one connection of the map, drawn as the kind of its part says: a command or query goes from the caller to the target, and a dashed arrow brings the result of a query back; an event goes from the provider that raises it to the caller that receives it, with an open arrowhead. A bar is the time a lifeline is busy with a step; it ends when a lifeline further out makes the next step, and a unit below the busy one acts for it. An event from an idle lifeline lands on the bar of a busy receiver, or starts one. A step shows its result; a note on a provider's lifeline shows the state of a connection whose contract has states.

```mermaid
---
config:
  sequence:
    height: 108
---
sequenceDiagram
  participant pslugify as slugify<br/>Turn a string into a slug
  participant pcore as core<br/>«logic»<br/>Makes slugs and defines what a<br/>transliteration plug-in must<br/>provide
  participant pplugin_dapi as plugin-api<br/>The trait through which a caller<br/>supplies transliteration
  pslugify->>pcore: 1 · slugify-with(#quot;Straße#quot;, default, plugin)
  activate pcore
  pcore-->>pslugify: ↩ 1 · strasse
  deactivate pcore
  pplugin_dapi->>pcore: 2 · transliterate('ß') → ss
  Note over pslugify,pplugin_dapi: wrap: Expect: `slugify_with(#quot;Straße#quot;, &Options::default(), &plugin)` returns `strasse` when the plug-in answers `ss` for `ß`
```

| # | Caller | Target | Call | Kind | Result | State | Contract |
|---|---|---|---|---|---|---|---|
| 1 | `slugify` | `core` | `slugify-with("Straße", default, plugin)` | query | strasse |  | [slugify](../references/slugify.md) |
| 2 | `plugin-api` | `core` | `transliterate('ß')` | type | ss |  | [plugin-api](../references/plugin-api.md) |
