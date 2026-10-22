# Break the map

This lesson is for a developer who has done [three commands](three-commands.md). You make the map and the code disagree twice and read what `check` reports. Work in the folder `examples/slugline`, with `unifold` set as the alias from [README.md](../../README.md).

1. Delete the line `cli.transliteration: unicode.transliteration` from [unifold.yaml](../../unifold.yaml).

2. Run `unifold check`. It reports three errors and a warning:

   ```console
   $ unifold check
   error G1 docs/diagrams/component.md: generated file is out of date
       fix: Run `unifold generate` (or `unifold check --fix`). A hand-written `AGENTS.md` is not overwritten: move its content to `README.md` and `docs/`, delete it, then run the command.
   error D1 unifold.yaml:21: 'cli' depends on 'plugins/unicode', but no need of 'cli' is connected to 'unicode' (cargo: cli/Cargo.toml [dependencies] slugline-unicode)
       fix: Wire need `transliteration` of cli/unifold.yaml, which is declared but not connected: add `cli.transliteration: unicode.transliteration` to the wiring here. Or remove the dependency from the code.
   error W2 unifold.yaml:21: need 'cli.transliteration' has no provider
       fix: Add `cli.transliteration: unicode.transliteration` to the wiring.
   warn W3 unifold.yaml:21: 'unicode.transliteration' is provided but nothing uses it
       fix: Wire the unit that should use it, or implement a capability of the parent with it (`capability: child.capability`), or remove the capability.
   4 unit(s): 3 error(s), 1 warning(s), 0 info  [D1×1, G1×1, W2×1, W3×1]; 3 dependencies observed in code
   ```

   `D1` says that the code of `cli` depends on `unicode` without a connection. `W2` says that the need has no provider.

3. Put the line back. Run `unifold check`. It prints `0 error(s), 0 warning(s)` again.

4. Append these lines to `core/Cargo.toml`:

   ```toml
   [dependencies]
   slugline-unicode = { path = "../plugins/unicode" }
   ```

5. Run `unifold check`. It reports one error:

   ```console
   $ unifold check
   error D1 unifold.yaml:21: 'core' depends on 'plugins/unicode', but no need of 'core' is connected to 'unicode' (cargo: core/Cargo.toml [dependencies] slugline-unicode)
       fix: Add a need to core/unifold.yaml (for example `unicode`), and add `core.unicode: unicode.transliteration` to the wiring here. Or remove the dependency from the code.
   4 unit(s): 1 error(s), 0 warning(s), 0 info  [D1×1]; 4 dependencies observed in code
   ```

   No manifest of `core` has a need for this dependency. Cargo refuses this edit too, because it closes a cycle.

6. Remove the two lines again. Run `unifold check`. It prints `0 error(s), 0 warning(s)`.

You have seen how `check` reports a need without a provider and a dependency in code without a connection.
