# Writing rules for Markdown files

These rules apply to every Markdown file that youmedoc manages: `README.md`
and `AGENTS.md` of each unit and every `.md` file below a unit's `doc/`
folder. They do not apply to resources inside a skill's `assets/` and
`scripts/` folders, and not to other Markdown files in the repository.

## Length

A file has at most **200 lines**, front matter included.

The limit keeps every file small enough for a human to review in one sitting
and for an agent to read as a whole. When a file would grow beyond it:

- Split a reference into a folder with an `index.md` and parts
  ([doc-folder.md](doc-folder.md)). The index links to every part and says
  what each part contains.
- Move the long form of the why from `AGENTS.md` to `doc/architecture.md`.
- Move a procedure out of any other file into a skill.
- Ask whether the unit is too big. A `README.md` that does not fit usually
  describes a unit that should have children.

Do not get under the limit by making lines longer. Wrap prose at about 80
characters. Tables and links may exceed that.

## Links

Links are the connective tissue of a youmedoc project. Use them extensively.

- Whenever a file mentions another file, a decision, a reference, a skill or
  a diagram, the mention MUST be a link. One exception: a file of a unit
  below the root names the standard and its three skills without a relative
  link, for example "the `check-docs` skill", or links to the published
  standard by its URL.
- Links between files are relative. Absolute paths and links that start with
  `/` are not allowed. Links to the outside world are full URLs.
- Every file below `doc/` MUST be reachable by links from the unit's
  `README.md` or `AGENTS.md`. A file nobody links to is lost.
- Where a link may point is restricted by the reference-direction rules in
  [rules.md](rules.md). In short: within the unit freely; down only to a
  direct child's `README.md`; up only from `doc/context.md`; never sideways.
- Link text says what the target is. Do not write "click here".
- Refer to units and ports of the same unit by name in `code font`. They need
  no link, because the manifest is in the same folder.

## Structure

- A file starts with a single `# ` title, after the front matter if it has
  any. Generated files have the marker comment before the title.
- Use `##` and `###` for sections. Do not skip levels.
- Use the section names that [unit-files.md](unit-files.md) and
  [doc-folder.md](doc-folder.md) give, in the given order. Readers and tools
  rely on them.
- Use tables for things with the same attributes and lists for sequences and
  enumerations. Use prose for reasons.
- Code blocks state their language.

## Style

The files are read by people and by models. The same style serves both.

- State facts. Write "The gateway rejects uploads larger than 1 MB", not
  "Uploads should probably be kept small".
- Put the main statement first, then the reason, then the detail.
- One term for one thing. Define project terms once, in a glossary reference,
  and use them unchanged.
- Present tense for what is, also for a unit with `status: planned`. The
  status field says that it is a plan.
- No history. A document describes the current state. What changed and why is
  in the decisions and in version control.
- No filler: no introductions that repeat the title, no summaries that repeat
  the body.
- Name the actor. "The ingest service validates the payload", not "The
  payload is validated".
- Write so that a reader who opens only this file can follow it. Do not write
  "as described above in another file"; link.

## Front matter

- `README.md` of a unit carries the [manifest](manifest.md).
- Decision records and `SKILL.md` files carry the front matter that
  [doc-folder.md](doc-folder.md) defines.
- Other files have no front matter.

## File names

- Fixed names are given by the standard: `README.md`, `AGENTS.md`,
  `context.md`, `architecture.md`, `index.md`, `SKILL.md`.
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
