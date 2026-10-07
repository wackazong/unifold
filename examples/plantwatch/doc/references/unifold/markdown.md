# Writing rules for Markdown files

These rules apply to every Markdown file that unifold manages: `README.md`
and `AGENTS.md` of each unit and the `.md` files in the entries of a unit's
`doc/` folder that [doc-folder.md](doc-folder.md) defines. They do not apply
to resources inside a skill's `assets/` and `scripts/` folders, and not to
other Markdown files in the repository.

## Length

A file has at most **200 lines**, front matter included (`T1`).

The limit keeps every file small enough for a human to review in one sitting
and for an agent to read as a whole. When a file would grow beyond it:

- Split a reference into a folder with an `index.md` and parts
  ([doc-folder.md](doc-folder.md)).
- Move the long form of the why from `AGENTS.md` to `doc/architecture.md`.
- Move a procedure out of any other file into a skill.
- Ask whether the unit is too big. A `README.md` that does not fit usually
  describes a unit that should have children.

Do not get under the limit by making lines longer. Wrap prose at about 80
characters. A line of more than 400 characters is reported (`T3`); it is hard
to review and hides in a line-based comparison. Long table cells are the
usual cause: turn the table into short sections.

## Links

Links are the connective tissue of a unifold project. Use them extensively.

- Whenever a file mentions another file, a decision, a reference, a skill or
  a diagram, the mention MUST be a link. One exception: a file of a unit
  below the root names the standard and its three skills without a relative
  link, for example "the `check-docs` skill", or links to the published
  standard by its URL.
- Links between files are relative. Absolute paths and links that start with
  `/` are not allowed. Links to the outside world are full URLs.
- Every managed file MUST be reachable by links from the unit's `README.md`
  or `AGENTS.md` (`L5`). A file nobody links to is lost.
- Where a link may point is restricted by the reference-direction rules in
  [rules.md](rules.md). In short: within the unit freely; down only to a
  direct child's `README.md`; up only from `doc/context.md`; never sideways.
- Link text says what the target is. Do not write "click here".

## Names of units and ports

- The name of a unit or port in running text is written in `code font`. The
  everyday word that happens to be the same is not. This is how a reader, and
  the checker, tells "the `store` unit" from "a store of readings".
- A unit's files use in code font only the names of the unit itself, its
  ports and its children. The name of a sibling or an ancestor in code font
  outside `doc/context.md` is reported (`L6`).
- Ports and children of the same unit need no link; the manifest is in the
  same folder.

## Structure

- A file starts with a single `# ` title, after the front matter if it has
  any. Generated files have the marker comment before the title.
- Use `##` and `###` for sections. Do not skip levels.
- Use the section names that [unit-files.md](unit-files.md) and
  [doc-folder.md](doc-folder.md) give, in the given order. Readers and tools
  rely on them.
- Use tables for things with the same short attributes and lists for
  sequences and enumerations. Use prose for reasons.
- Code blocks state their language.

## Style

The files are read by people and by models. The same style serves both.

- State facts. Write "The gateway rejects uploads larger than 1 MB", not
  "Uploads should probably be kept small".
- Put the main statement first, then the reason, then the detail.
- One term for one thing within a unit. Define the terms of a unit once, in
  its glossary, and use them unchanged
  ([principles.md](principles.md)).
- Write guarantees so that they can be checked: a value, a limit, an order.
- Present tense for what is, also for a unit with `status: planned`. The
  status field says that it is a plan.
- No history. A document describes the current state. What changed and why is
  in the decisions and in version control.
- No filler: no introductions that repeat the title, no summaries that repeat
  the body.
- Name the actor. "The ingest service validates the payload", not "The
  payload is validated".
- Write so that a reader who opens only this file can follow it.

## Front matter

- `README.md` of a unit carries the [manifest](manifest.md), unless the unit
  has a `unit.yaml`.
- Decision records and `SKILL.md` files carry the front matter that
  [doc-folder.md](doc-folder.md) defines.
- Other files have no front matter.

## File names

- Fixed names are given by the standard: `README.md`, `AGENTS.md`,
  `unit.yaml`, `context.md`, `architecture.md`, `index.md`, `glossary.md`,
  `SKILL.md`.
- All other file and folder names use lower-case letters, digits and `-`.
- Name a file after its content: `ble-profile.md`, not `notes.md`.

## What an agent does before saving a file

1. Count the lines. More than 200: split.
2. Check every mention of another file: is it a link, and does the link obey
   the direction rules?
3. Check that the file is linked from somewhere in the unit.
4. Check that no fact in the file is already stated in another file of the
   project. If it is, link instead.
5. Run the [checker](checker.md).
