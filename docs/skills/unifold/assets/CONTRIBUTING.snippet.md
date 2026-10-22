## Architecture map

This repository follows [unifold](https://unifold.md). Some folders are units: they contain a `unifold.yaml` that says what the folder provides and what it needs. The unit above connects each need to a provider in `wiring`.

When you change code:

1. Read the `unifold.yaml` of the folder you change, and its `README.md` if it has one; `AGENTS.md` says where its documents are.
2. If you add, remove or rename something that other folders use, or start to use another folder, change the manifest and the `wiring` in the manifest of the unit above.
3. Run the tool and commit what it writes:

   ```sh
   uv run docs/skills/unifold/scripts/unifold.py check --fix
   uv run docs/skills/unifold/scripts/unifold.py check
   ```

4. Do not edit files that start with `<!-- unifold:generated`.

A decision record is proposed in a pull request with `status: proposed`. A maintainer sets it to `accepted`.
