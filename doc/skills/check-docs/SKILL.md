---
name: check-docs
description: Check a youmedoc project against the ruleset - run the checker, fix what it reports, then review meaning by hand. Use it after every change to documents or folder structure, before a commit, and when asked to review or enforce youmedoc.
---
# Check the docs of a youmedoc project

The ruleset has two parts. A tool checks the mechanical part. You check the
part that concerns meaning. Both are required.

## Steps

1. **Generate.** From anywhere in the project run:

   ```sh
   uv run <root>/doc/skills/check-docs/scripts/youmedoc.py generate
   ```

   `<root>` is the project root. Without `uv`, use `python3` with PyYAML
   installed. Details: [checker.md](../../references/youmedoc/checker.md).

2. **Check.**

   ```sh
   uv run <root>/doc/skills/check-docs/scripts/youmedoc.py check
   ```

3. **Fix every error** (lines that start with `E`). The second word is the
   rule ID. Look it up in
   [rules-tool.md](../../references/youmedoc/rules-tool.md); the table at its
   end lists the usual fixes. Fix the cause, not the symptom:
   - Do not delete a need to silence `W2`. Wire it, or pass it up.
   - Do not move an upward link into a code span to silence `L3`. Cite the
     item in `doc/context.md`.
   - Do not shorten a file by joining lines to silence `T1`. Split it.

4. **Judge every warning** (lines that start with `W`). Fix it, or keep it
   and say why in your report.

5. **Repeat** steps 1 to 4 until no errors remain.

6. **Review meaning.** For every file you changed, and for every file a
   human asked you to review, go through the review rules in
   [rules-review.md](../../references/youmedoc/rules-review.md), `C1` to
   `C13`. The ones violated most often:
   - `C2`: the file names a sibling, the parent or a user of the unit.
   - `C3`: a parent restates what a child's `README.md` says.
   - `C4`: `AGENTS.md` or `doc/architecture.md` lists children or wiring.
   - `C5`: the unit relies on something from above that `doc/context.md`
     does not cite.
   - `C6`: the same fact is stated in two files.
   - `C13`: a need expects something its provider does not offer. Check
     this in every unit whose wiring or children changed.

7. **Report.** List findings as rule ID, file, problem, fix. State what you
   fixed and what you left for a human, in particular decisions that are
   still `proposed`.

## When you review someone else's change

Do steps 2 and 6 without changing files, and report. Do not fix silently.

## When the checker cannot run

Check by hand, in this order: every unit has `README.md` with a manifest and
`AGENTS.md`; every need of every child appears as a key in its parent's
`wiring`; no file exceeds 200 lines; no link points sideways or, outside
`doc/context.md`, upward. Say in your report that the tool did not run.

## Reference

- Overview of the ruleset and the direction rules:
  [rules.md](../../references/youmedoc/rules.md)
- The tool: [youmedoc.py](scripts/youmedoc.py)
