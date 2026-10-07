# Contributing to plantwatch

plantwatch is documented with [unifold](https://unifold.md). Some
folders are units: they have a `unit.yaml` that says what the unit provides
and needs, a `README.md` that describes it from outside, and an `AGENTS.md`
that says why it is built the way it is.

## If you change something in a unit

1. Read the `README.md` and the `AGENTS.md` of the unit.
2. Make your change.
3. If behaviour that the `README.md` promises changed, change the
   `README.md`. If a port or a need was added, removed or renamed, change
   the `unit.yaml` of the unit and the `wiring` in the `unit.yaml` of the
   folder above.
4. If you change a number that documents state, such as a limit or a
   default, find the other places: run `show` on the unit to see who uses
   its ports, run `cited-by` on the file that defines the number, and search
   the repository for the old value in every notation (15 minutes, 900 s).
5. Run the generator and the checker and commit the regenerated files with
   your change:

   ```sh
   python3 doc/skills/check-docs/scripts/unifold.py generate
   python3 doc/skills/check-docs/scripts/unifold.py check
   ```

   The tool needs Python 3.9 or newer with PyYAML. `uv run` instead of
   `python3` fetches PyYAML by itself.

## Decisions

Choices with alternatives are recorded in `doc/decisions/` of the unit they
concern, with `status: proposed`. A maintainer accepts a decision by setting
`status: accepted` and naming the decision-makers. Every decision in this
example is still `proposed`.

## Rules you will meet

- A file has at most 200 lines.
- A unit does not name or link to its neighbours. What it wants from them is
  a need in its `unit.yaml`.
- Files in `doc/diagrams/` and `doc/decisions/index.md` are generated. Do not
  edit them.

The rules are explained in
[doc/references/unifold/index.md](doc/references/unifold/index.md).
