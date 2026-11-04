# Writing the documents

[documents.md](documents.md) says which files a unit has. This chapter says how each is written, what a reviewer checks, and the style they share. [decision-records.md](decision-records.md) says how a decision and a context item are written, and [contracts.md](contracts.md) how a contract is written. What each explanation file holds is in [documents.md](documents.md).

## References and the glossary

A reference is `docs/references/<topic>.md`: facts as they are now, for example a contract ([contracts.md](contracts.md)), a part of one, or a convention that several contracts share. It gives no reasons; where a decision settled a fact, it may link that decision. Procedures go to skills. Notes about the work stay with the process that does the work. A reference that would exceed the word limit becomes a folder with an `index.md` that links to every part. For a contract, `docs/references/<topic>/index.md` holds every section, with `## Parts` as a list of links in the order of use, and every part is a file `<topic>/<part>.md` with the body of a `###` section; the manifests name `index.md`, and a part name resolves to a heading in the file or to a file in the folder. API reference that a tool produces from code is not written by hand. `docs/references/glossary.md` holds the terms that have one fixed meaning inside the unit, one table row per term, so that each can be cited alone. A term is defined in the lowest unit that covers its uses.

`docs/references/constants.md` holds the fixed values a unit and the units below it use: a table whose first columns are `Name` and `Value`, one row per value, named everywhere else and written out only there, such as `MAX_PAYLOAD`. A column `Source` MAY say where a value comes from, such as `proto §4.2`.

## Skills

A skill is a how-to guide for a recurring task in the unit, in the [Agent Skills](https://agentskills.io/specification) format: `docs/skills/<name>/SKILL.md`, with a front matter that has `name`, equal to the folder name, and `description`. The description says for whom the procedure is, when it is written for an end user.

- A skill belongs to the lowest unit in which the whole procedure happens. `unifold show` lists the skills of a unit, and `unifold skills` those of the project.
- `unifold check --fix` writes a generated stub for each skill where agents search for skills ([agents.md](agents.md)). The source stays here.
- A person reviews a skill that an agent wrote before others rely on it.

## Tutorials

A tutorial is `docs/tutorials/<name>.md`: a lesson that leads one stated reader, for example "a developer who has cloned the repository" or "an owner with a new sensor stick", through numbered steps to one result they can see. It uses one concrete example throughout, says at each step what the reader should now observe, and explains nothing that is not needed to take the next step. What a thing is belongs in a reference; why it is so in an explanation; both are linked, not repeated. A tutorial is tried by a person before others rely on it.

## Review checklist

The checker compares files with each other. Whoever reviews a change, a person or an agent, checks the meaning:

1. Can the unit be used after reading its `README.md` and the contracts that its manifest names?
2. For each changed connection, does the provider cover what the need expects? `unifold capability` prints both sides. Do the examples of each part cover its errors and both sides of every precondition?
3. Does a file name a sibling or a user, or restate what another file states? Write the need or the capability, or link the file.
4. Is a changed name or value stated elsewhere? Search for the old one.
5. Does every document describe the unit as it is now, and does `status` match reality? Did anything set a decision to `accepted` without a person asking for it?
6. Does a human reader understand each document easily ([Plain language](#plain-language))?

## Plain language

Write every document in language that a human reader understands easily.

## Markdown style

- A hand-written file has at most 1,500 words, not counting its front matter, and `## Why` of a `README.md` at most 250. Before one grows beyond that, split the reference, or move the long why to `docs/explanation/reasoning.md` or a procedure into a skill. Or ask whether the unit is too big. Write one line per paragraph and per list item; nobody wraps prose by hand.
- A mention of another file SHOULD be a link whose text says what the target is. Units, capabilities and needs are named in code font. A file has one `#` title; `##` and `###` follow without skipping a level.
- One term for one thing: the term of [spec.md](spec.md) section 1 or of the unit's glossary, never a synonym. A unit *provides* and *needs*; the parent *connects*. Not "offers" or "exposes" for provides, not "depends on" for needs.
- YAML in a manifest is written in block style, one key per line; the short form `name: one-line summary` for a capability or need stays. Flow style, `{...}`, is valid and the checker does not care, but a value that contains `:` or a comma must then be quoted.

What the reference tool reports is in [rules.md](rules.md).
