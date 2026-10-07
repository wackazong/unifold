<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Context diagram: slugline

**slugline** · [README](../../README.md) · [component](component.md) · [architecture](architecture.md)

`slugline` and the outside world: the ports it provides (rounded) and the things it needs from outside (hexagons).

```mermaid
flowchart LR
  u_root["slugline"]
  p_root___slugify(["slugify"])
  p_root___slugify --> u_root
  p_root___slug_dcli(["slug-cli"])
  p_root___slug_dcli --> u_root
  classDef focus stroke-width:4px
  class u_root focus
```

| Port | Direction | Kind | Summary |
|---|---|---|---|
| slugify | provided | library | Turn a string into a slug |
| slug-cli | provided | cli | Slugs on the command line |
