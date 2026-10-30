<!-- unifold:generated - do not edit; run `unifold generate` -->
# Scenario: library-call

**slugline** · [README](../../README.md) · [component](component.md)

**A program calls the library with a plug-in of its own**
Source: the tests of core
Expect: `slugify_with("Straße", &Options::default(), &plugin)` returns `strasse` when the plug-in answers `ss` for `ß`

A unit is named by its path from `slugline`; a capability or need of `slugline` is named bare. Every hop is a call along one connection of the map.

```mermaid
---
config:
  sequence:
    height: 108
---
sequenceDiagram
  participant pslugify as slugify<br/>«library»<br/>Turn a string into a slug
  participant pcore as core<br/>«logic»<br/>Makes slugs and defines what a<br/>transliteration plug-in must<br/>provide
  participant pplugin_dapi as plugin-api<br/>«library»<br/>The trait through which a caller<br/>supplies transliteration
  pslugify->>pcore: 1 · slugify-with
  pplugin_dapi->>pcore: 2 · transliterate
  Note over pslugify,pplugin_dapi: wrap: Expect: `slugify_with(#quot;Straße#quot;, &Options::default(), &plugin)` returns `strasse` when the plug-in answers `ss` for `ß`
```

| # | Caller | Target | Part | Contract |
|---|---|---|---|---|
| 1 | `slugify` | `core` | `slugify-with` | [slugify](../references/slugify.md) |
| 2 | `plugin-api` | `core` | `transliterate` | [plugin-api](../references/plugin-api.md) |
