<!-- youmedoc:generated - do not edit; run `youmedoc generate` -->
# Context diagram: youmedoc

**youmedoc** · [README](../../README.md)

`youmedoc` and the outside world: the ports it provides (rounded) and the things it needs from outside (hexagons).

```mermaid
flowchart LR
  u_root["youmedoc"]
  p_root___specification(["specification"])
  p_root___specification --> u_root
  p_root___skills(["skills"])
  p_root___skills --> u_root
  p_root___checker(["checker"])
  p_root___checker --> u_root
  n_root___python{{"python"}}
  u_root --> n_root___python
  classDef focus stroke-width:4px
  class u_root focus
```

| Port | Direction | Kind | Summary |
|---|---|---|---|
| specification | provided | specification | The text of the standard, in chapters of at most 200 lines |
| skills | provided | skill | Three skills that teach an agent to read, write and check a youmedoc project |
| checker | provided | cli | Reference tool that checks the mechanical rules, describes units and generates diagrams |
| python | needed | runtime | Python 3.9 or newer with PyYAML, to run the checker |
