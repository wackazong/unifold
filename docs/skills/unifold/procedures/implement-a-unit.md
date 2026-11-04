# Implement a unit from its contracts

1. Run `unifold brief PATH`. It prints what to implement (the parts of each capability, with signature, `Pre:`, `Result:`, `Errors:` and examples), what to fake (each need, with its parts and the `## Fake` of its contract), the states, the scenarios through the unit, the constants and the context items. Read the `## Why` of `README.md`.
2. Write one test per example row first, named after the row's id, `<contract>#<part>/<case-slug>`, in the test's name or in a comment beside it. A row with `Given` sets that state first. Where `## States` exists, one test walks the table.
3. Write the stand-ins for the needs as their contracts' `## Fake` says: a replay of the examples, the simplified behaviour with its faults, or the real unit where the fake is `the real implementation`.
4. Implement until the tests pass. Where a contract and the code cannot agree, change the contract and its examples, never only the test ([change-an-interface.md](change-an-interface.md)).
5. Run `unifold trace PATH`. It lists the examples that no test names and the ids that no example has. Leave none.
6. Set `status: active` in the manifest when the unit does what its contracts say. [Finish](../SKILL.md#4-finish).
