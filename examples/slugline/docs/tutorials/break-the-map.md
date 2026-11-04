# Break the map

This lesson is for a developer who has done [three commands](three-commands.md). You break the map twice and read what `check` reports. Work in the folder `examples/slugline`, with `unifold` set as the alias from [README.md](../../README.md).

1. Delete the line `cli.transliteration: unicode.transliteration` from [unifold.yaml](../../unifold.yaml).

2. Run `unifold check`. It reports three errors and a warning:

   ```console
   $ unifold check
   error G1 docs/diagrams/component.md: generated file is out of date
       fix: Run `unifold check --fix`. A hand-written `AGENTS.md` at the root is not overwritten: move its content to `README.md` and `docs/`, delete it, then run the command.
   error W2 unifold.yaml:19: need 'cli.transliteration' has no provider
       fix: Add `cli.transliteration: unicode.transliteration` to the wiring.
   warn W3 unifold.yaml:19: 'unicode.transliteration' is provided but nothing uses it
       fix: Wire the unit that should use it; where code of the parent itself uses it, declare a need in the parent and wire it (`need: child.capability`); or implement a capability of the parent with it (`capability: child.capability`); or remove the capability.
   error N1 unifold.yaml:26: scenario 'slug-from-arguments', hop 'cli -> plugins/unicode.latin()': no need of 'cli' is provided for by 'plugins/unicode'
       fix: Wire the connection the hop needs, add the part to the contract, or write `target.capability.part`.
   4 unit(s): 3 error(s), 1 warning(s), 0 info  [G1×1, N1×1, W2×1, W3×1]
   ```

   `W2` says that the need of `cli` has no provider. `W3` says the same from the other side: nothing uses the capability of `unicode`. `N1` says that the story `slug-from-arguments` can no longer run: its hop from `cli` to the plug-in has no connection to run along. `G1` says that the component diagram no longer matches the manifests.

3. Put the line back. Run `unifold check`. It prints `0 error(s), 0 warning(s)` again.

4. In `plugins/unicode/unifold.yaml`, change the contract of the need `plugin-api` to `../../docs/references/slug.md`.

5. Run `unifold check`. It reports two errors and three warnings:

   ```console
   $ unifold check
   warn C1 docs/references/slug.md: no `## Parts` section; a contract lists its parts, one `###` heading each
       fix: Write the parts as [contracts.md](contracts.md#parts) says.
   warn C5 docs/references/slug.md: no `## Fake` section: say what stands in for this contract in the tests of its consumers
       fix: Say what stands in for the contract in the tests of its consumers.
   warn C6 docs/references/slug.md: no `## Use` section: say what a consumer does with the connection
       fix: Say how a consumer uses the connection: in which order it calls the parts, what it does when a call fails, and the rules that hold for every part.
   error W11 unifold.yaml:25: need 'unicode.plugin-api' names the contract docs/references/slug.md, capability 'core.plugin-api' names docs/references/plugin-api.md
       fix: Write the definition as a reference of this unit, the one that holds the wiring, or of a unit above it, and point both sides at it with `contract`.
   error N1 unifold.yaml:27: scenario 'slug-from-arguments', hop 'core -> plugins/unicode.transliterate('è')': part 'transliterate' is not in the contract docs/references/slug.md
       fix: Wire the connection the hop needs, add the part to the contract, or write `target.capability.part`.
   4 unit(s): 2 error(s), 3 warning(s), 0 info  [C1×1, C5×1, C6×1, N1×1, W11×1]
   ```

   The two sides of one connection now name different documents, so they no longer agree on what travels between them (`W11`). The document the need names is a reference, not a contract: it has no parts, no fake and no use section (`C1`, `C5`, `C6`), so the hop of the scenario in which `core` calls the plug-in finds no part `transliterate` in it (`N1`).

6. Change the contract back to `../../docs/references/plugin-api.md`. Run `unifold check`. It prints `0 error(s), 0 warning(s)`.

You have seen how `check` reports a need without a provider, a connection whose sides name different contracts, and a story that can no longer run. It reads no code: a `Cargo.toml` that uses another crate without a need is for you and your review to notice.
