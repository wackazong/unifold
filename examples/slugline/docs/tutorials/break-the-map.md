# Break the map

This lesson is for a developer who has done [three commands](three-commands.md). You break the map twice and read what `check` reports. Work in the folder `examples/slugline`, with `unifold` set as the alias from [README.md](../../README.md).

1. Delete the line `cli.transliteration: unicode.transliteration` from [unifold.yaml](../../unifold.yaml).

2. Run `unifold check`. It reports two errors and a warning:

   ```console
   $ unifold check
   error G1 docs/diagrams/component.md: generated file is out of date
       fix: Run `unifold generate` (or `unifold check --fix`). A hand-written `AGENTS.md` is not overwritten: move its content to `README.md` and `docs/`, delete it, then run the command.
   error W2 unifold.yaml:21: need 'cli.transliteration' has no provider
       fix: Add `cli.transliteration: unicode.transliteration` to the wiring.
   warn W3 unifold.yaml:21: 'unicode.transliteration' is provided but nothing uses it
       fix: Wire the unit that should use it; where code of the parent itself uses it, declare a need in the parent and wire it (`need: child.capability`); or implement a capability of the parent with it (`capability: child.capability`); or remove the capability.
   4 unit(s): 2 error(s), 1 warning(s), 0 info  [G1×1, W2×1, W3×1]
   ```

   `W2` says that the need of `cli` has no provider. `W3` says the same from the other side: nothing uses the capability of `unicode`. `G1` says that the diagram no longer matches the manifests.

3. Put the line back. Run `unifold check`. It prints `0 error(s), 0 warning(s)` again.

4. In `plugins/unicode/unifold.yaml`, change the contract of the need `plugin-api` to `../../docs/references/slug.md`.

5. Run `unifold check`. It reports one error:

   ```console
   $ unifold check
   error W11 unifold.yaml:27: need 'unicode.plugin-api' names the contract docs/references/slug.md, capability 'core.plugin-api' names docs/references/plugin-api.md
       fix: Write the definition as a reference of this unit, the one that holds the wiring, or of a unit above it, and point both sides at it with `contract`.
   4 unit(s): 1 error(s), 0 warning(s), 0 info  [W11×1]
   ```

   The two sides of one connection now name different documents, so they no longer agree on what travels between them.

6. Change the contract back to `../../docs/references/plugin-api.md`. Run `unifold check`. It prints `0 error(s), 0 warning(s)`.

You have seen how `check` reports a need without a provider and a connection whose sides name different contracts. It reads no code: a `Cargo.toml` that uses another crate without a need is for you and your review to notice.
