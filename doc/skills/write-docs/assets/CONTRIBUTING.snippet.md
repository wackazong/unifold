## Documentation

This repository is documented with [unifold](https://unifold.md). Some
folders are units: they have a manifest (`unit.yaml` or the front matter of
`README.md`), a `README.md` that describes what the folder provides and needs,
and an `AGENTS.md` that says why it is built as it is.

When you change code:

1. Read the `README.md` and `AGENTS.md` of the unit you change.
2. If you change behaviour that the `README.md` promises, change the
   `README.md` in the same commit.
3. If you add, remove or rename a port, change the manifest of the unit and
   the `wiring` in the manifest of its parent.
4. Run the generator and the checker and commit the regenerated files:

   ```sh
   uv run doc/skills/check-docs/scripts/unifold.py generate
   uv run doc/skills/check-docs/scripts/unifold.py check
   ```

5. Do not edit files in `doc/diagrams/` or any `doc/decisions/index.md`; they
   are generated.

A decision record is proposed in a pull request with `status: proposed`. A
maintainer sets it to `accepted`.
