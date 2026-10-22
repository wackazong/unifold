<!-- unifold:generated - do not edit; run `unifold generate` -->
# Component diagram: slugline

**slugline** · [README](../../README.md)

The units directly inside `slugline` and how they are connected. An arrow points from the unit that needs something to the unit that provides it. Rounded nodes are capabilities of the framing unit, hexagons are its needs. A dashed arrow is an alternative provider; a dashed border marks a unit that is planned.

```mermaid
flowchart LR
  subgraph u_root["slugline"]
    u_cli["cli"]
    u_core["core"]
    u_plugins__unicode["unicode"]
  end
  p_root___slugify(["slugify"])
  p_root___plugin_dapi(["plugin-api"])
  p_root___slugline_dcommand(["slugline-command"])
  u_cli -->|"slugify"| u_core
  u_cli -->|"transliteration"| u_plugins__unicode
  u_plugins__unicode -->|"plugin-api"| u_core
  p_root___slugify --> u_core
  p_root___plugin_dapi --> u_core
  p_root___slugline_dcommand --> u_cli
  classDef focus stroke-width:4px
  classDef planned stroke-dasharray:6 4
  classDef deprecated stroke-dasharray:2 2,opacity:0.6
  classDef plain stroke-dasharray:2 3
```

| Unit | Kind | Summary | Status |
|---|---|---|---|
| cli | app | The slugline command | active |
| [core](../../core/README.md) | library | Makes slugs and defines what a transliteration plug-in must offer | active |
| unicode | library | Transliterates Latin letters with diacritics to ASCII | active |

### Connections

| Need | Provider | Note |
|---|---|---|
| capability `slugify` of `slugline` | `core.slugify` | implemented by |
| capability `plugin-api` of `slugline` | `core.plugin-api` | implemented by |
| capability `slugline-command` of `slugline` | `cli.slugline-command` | implemented by |
| `cli.slugify` | `core.slugify` |  |
| `cli.transliteration` | `unicode.transliteration` |  |
| `unicode.plugin-api` | `core.plugin-api` |  |
