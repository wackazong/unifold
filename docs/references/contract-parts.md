# Parts of a contract

A part is one operation, event or type of a [contract](contracts.md). This chapter is the standard for the parts: their names, kinds, signatures, examples and types. The parts stand in the order in which a consumer uses them. What the checker reads of a part is listed in [spec-conformance.md](spec-conformance.md#5-documents).

## Names

The name of a part is the anchor of its `###` heading: the heading in lower case, with spaces as `-` and everything but ASCII letters, digits, `-` and `_` dropped. In a contract folder it is the file name without `.md` ([writing.md](writing.md#references-and-the-glossary)). The manifests of the units that use only some of the parts list those names under `parts`:

```yaml
needs:
  frames:
    summary: Frames for the line
    contract:
      path: ../docs/references/frames.md
      parts:
        - encode
        - frame
```

## Kinds

Every part SHOULD have a line `Kind:` with one of these three kinds, and a signature:

| Kind | What it is | Has |
|---|---|---|
| `operation` | A call from the consumer to the provider, which answers | signature, `Pre:`, `Result:`, `Errors:`, `Examples:` |
| `event` | Something the provider emits and a consumer receives | signature, `When:` (what raises it), `Delivery:` (at-most-once, at-least-once or exactly-once, and the order key), `Examples:` |
| `type` | A record, variant or resource the parts share | signature, a table of fields or cases where they need words |

An operation SHOULD have `Pre:`, `Result:`, `Errors:` and an `Examples:` table. An event SHOULD have `When:` and `Delivery:`. A call that goes the other way, such as a plug-in that the provider asks or a handler it calls, is a connection of its own in that direction: the unit that is called provides it as a capability, and the unit that calls needs it.

## Signature

The signature is a fenced code block. The notation is named once in the header of the contract; the default is [WIT](https://component-model.bytecodealliance.org/design/wit.html), the interface language of the WebAssembly component model. WIT is plain text and language-neutral, and it has records, variants, enums, `result<T, E>`, `option<T>`, `list<T>` and resources with methods. Any other notation is allowed, for example an OpenAPI fragment, a `.proto` message or a signature in the project's own language.

## Examples

Examples are the first tests of the provider and the whole behaviour of a replay fake ([contracts.md](contracts.md#the-fake)).

- **Columns.** The `Examples:` table of an operation SHOULD have the columns `Case | Input | Expected`, or `Case | Given | Input | Expected` where a row needs a state of the connection or of a fake first, and at least one row. The table of an event, where it has one, SHOULD have the columns `Case | Action | Emitted`, or the same with `Given` before `Action`.
- **Cells.** `Input` is a call in the notation of the signature. `Expected` is its result: a value, `ok`, or an error case that `Errors:` names. `Errors:` names each error case once in code font; the condition after it is written without code font.
- **Case.** The `Case` names the row and SHOULD be unique within the part. Where a source gives the vector, name it there too: `empty payload, proto §4.2`.
- **Id.** The id of an example is `<contract>#<part>/<case-slug>`, for example `frames#encode/empty-payload-proto-42`, with the slug formed like the anchor of a heading. A test that proves the example names the id, and `unifold trace` lists the examples that no test names ([tool.md](tool.md#brief-and-trace)).
- **Coverage.** Boundaries on both sides of every `Pre:` and one row per error make the table complete enough that two people would write the same tests.

## Types

A type SHOULD be defined once within the subtree of the unit that holds the contract. A contract that uses a type of another contract links to its definition instead of repeating it. A type SHOULD be used: a part names it in its signature, a manifest lists it under `parts`, or a contract links to it. Remove a type that nothing uses.
