---
name: check-docs
description: Check a youmedoc project against the ruleset - run the checker, fix what it reports, then review meaning by hand. Use it after every change to documents or folder structure, before a commit, and when asked to review or enforce youmedoc.
license: MIT OR Apache-2.0
---
# Check the docs of a youmedoc project

The ruleset has two parts. A tool checks the mechanical part. You check the
part that concerns meaning. Both are required. A run of the tool without
findings means the documents agree with each other, not that they are right.

## Steps

1. **Generate, then check.** From anywhere in the project:

   ```sh
   uv run <root>/doc/skills/check-docs/scripts/youmedoc.py generate
   uv run <root>/doc/skills/check-docs/scripts/youmedoc.py check
   ```

   `<root>` is the project root. Without `uv`, use `python3` with PyYAML
   installed. Details: [checker.md](../../references/youmedoc/checker.md).

2. **Fix every error** (lines that start with `E`). The second word is the
   rule ID. Look it up in
   [rules-tool.md](../../references/youmedoc/rules-tool.md); the table at its
   end lists the usual fixes. Fix the cause, not the symptom:
   - Do not delete a need, or mark it `optional`, to silence `W2`. Wire it,
     or pass it up.
   - Do not move an upward link into a code span to silence `L3`. Cite the
     item in `doc/context.md`.
   - Do not shorten a file by joining lines to silence `T1`. Split it.
   - Do not change the kind of a need to silence `W4`. Add an adapter.

3. **Judge every warning** (lines that start with `W`). Fix it, or keep it
   and say why in your report.

4. **Repeat** steps 1 to 3 until no errors remain.

5. **Review meaning.** Apply the review rules in
   [rules-review.md](../../references/youmedoc/rules-review.md) that belong
   to what changed:

   | What changed | Rules to apply |
   |---|---|
   | A manifest: ports, needs, wiring | `C1`, `C12`, `C13`, `C14`; `C10` if code exists |
   | The body of a `README.md` | `C1`, `C2`, `C3`, `C6`, `C15` |
   | `AGENTS.md` or `doc/architecture.md` | `C2`, `C4`, `C6`, `C14` |
   | `doc/context.md`, or a file that others cite | `C5` |
   | A decision | `C7`, `C8` |
   | A reference or a skill | `C6`, `C8`, `C9`, `C15` for contracts |
   | A new unit or a moved folder | all of the above, and `C11` |

   How to apply the ones that need a method:
   - `C2`: search the unit's files for the names of its siblings and
     ancestors; `show` lists them as parent, providers and users.
   - `C5`: after a cited file changed, run `cited-by` on it and compare each
     restatement with the source.
   - `C6`: for each number with a unit and each identifier in a changed
     paragraph, search the project.
   - `C7`: compare changed decision files with version control, for example
     `git diff -- '*/doc/decisions/*'`. No change may set `accepted` unless a
     human asked for exactly that.
   - `C13`: for each changed wiring line, run `youmedoc port <unit folder>
     <port>`. It prints the need's text and the provider's text with their
     contracts, side by side.

6. **Report.** List findings as rule ID, file, problem, fix. State what you
   fixed and what you left for a human. List every change to an interface:
   ports, needs, `optional`, wiring lines, contracts. List the decisions
   that are still `proposed`.

## When you review someone else's change

Do steps 1 and 5 without changing files, and report. Do not fix silently.

## When the checker cannot run

Check by hand, in this order: every unit has a manifest, `README.md` and
`AGENTS.md`; every need of every child appears as a key in its parent's
`wiring`; no file exceeds 200 lines; no link points sideways or, outside
`doc/context.md`, upward. Say in your report that the tool did not run.

## Reference

- Overview of the ruleset and the direction rules:
  [rules.md](../../references/youmedoc/rules.md)
- The tool: [youmedoc.py](scripts/youmedoc.py)
