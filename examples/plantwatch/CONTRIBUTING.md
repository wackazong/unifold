# Contributing to plantwatch

plantwatch follows [unifold](https://unifold.md) 0.4. Some folders are units: they have a `unifold.yaml` that says what the unit provides and needs, and a `README.md` that describes it from outside and says why it is built the way it is. The generated `AGENTS.md` at the root points to the documents.

## If you change something in a unit

1. Read the `README.md` of the unit, and run `unifold show` in its folder.
2. Make your change.
3. If behaviour that a contract promises changed, change the contract: its parts, their examples and the fake. If what the `README.md` says changed, change the `README.md`. If a capability or a need was added, removed or renamed, change the `unifold.yaml` of the unit and the `wiring` in the `unifold.yaml` of the folder above.
4. If you change a number that documents state, such as a limit or a default, find the other places: run `show` on the unit to see who uses its capabilities, run `impact` on the file that defines the number, and search the repository for the old value in every notation (15 minutes, 900 s).
5. If you changed a file that context items cite, correct each item that is no longer true; `impact` on the file lists them.
6. Run the tool and commit what it writes with your change:

   ```sh
   unifold check --fix     # generated files
   unifold check
   ```

   `unifold` is the reference tool of the standard: `uvx unifold`, or `uv tool install unifold` to install it.

## Decisions

A new choice with alternatives is recorded in `docs/decisions/` of the unit it concerns, with `status: proposed`. A maintainer accepts a decision by setting `status: accepted` and naming the decision-makers. Every decision in force in this example is `accepted`.

## Rules you will meet

- A file has at most 1,500 words.
- A unit does not name or link to its siblings or its users. What it wants from them is a need in its `unifold.yaml`.
- Every `docs/decisions/index.md` and the root `AGENTS.md` are generated. Do not edit them.

The rules are explained at <https://unifold.md/rules>.
