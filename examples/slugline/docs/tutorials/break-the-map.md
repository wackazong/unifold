# Break the map

Two edits that make the map and the code disagree, and what `check` says. Undo each edit afterwards; `cargo test --workspace` and `unifold check` are green again.

**Remove a wiring line.** Delete `cli.transliteration: unicode.transliteration` from [unifold.yaml](../../unifold.yaml):

```console
$ unifold check
error G1 docs/diagrams/component.md: generated file is out of date
    fix: Run `unifold generate` (or `unifold check --fix`).
error D1 unifold.yaml:21: 'cli' depends on 'plugins/unicode', but no need of 'cli' is connected to 'unicode' (cargo: cli/Cargo.toml [dependencies] slugline-unicode)
    fix: Wire need `transliteration` of cli/unifold.yaml, which is declared but not connected: add `cli.transliteration: unicode.transliteration` to the wiring here. Or remove the dependency from the code.
error W2 unifold.yaml:21: need 'cli.transliteration' has no provider
    fix: Add `cli.transliteration: unicode.transliteration` to the wiring.
warn W3 unifold.yaml:21: 'unicode.transliteration' is provided but nothing uses it
    fix: Wire the unit that should use it, or implement a capability of the parent with it (`capability: child.capability`), or remove the capability.
4 unit(s): 3 error(s), 1 warning(s), 0 info  [D1×1, G1×1, W2×1, W3×1]; 3 dependencies observed in code
```

**Add a dependency that no manifest declares.** Let `core` use the table of the plug-in. Append to `core/Cargo.toml`:

```toml
[dependencies]
slugline-unicode = { path = "../plugins/unicode" }
```

```console
$ unifold check
error D1 unifold.yaml:21: 'core' depends on 'plugins/unicode', but no need of 'core' is connected to 'unicode' (cargo: core/Cargo.toml [dependencies] slugline-unicode)
    fix: Add a need to core/unifold.yaml (for example `unicode`), and add `core.unicode: unicode.transliteration` to the wiring here. Or remove the dependency from the code.
4 unit(s): 1 error(s), 0 warning(s), 0 info  [D1×1]; 4 dependencies observed in code
```

Cargo refuses this particular edit too, because it closes a cycle. unifold reports every dependency that is not wired, also those Cargo accepts.
