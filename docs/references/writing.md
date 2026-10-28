# Writing the documents

[documents.md](documents.md) says which files a unit has. This chapter says how each is written, what a reviewer checks, and the style they share.

## Context items and stamps

`docs/explanation/context.md` lists the decisions, conventions and terms from above that a reader must know to understand the unit. The repetition is deliberate: it keeps the unit understandable when its folder is read alone. Each item is a `###` heading:

```markdown
### [cloud/0002 Each service owns its data](../../../docs/decisions/0002-each-service-owns-its-data.md)
<!-- unifold:cites sha=3f9a1c2e -->

Says: no service reads or writes the database schema of another.

Here: `ingest` keeps its duplicate index in a schema of its own.
```

- The heading links to the source. **Cite the smallest part**: a fragment cites one section (`#heading`) or, where no heading has that anchor, one table row whose first cell gives it (`glossary.md#stamp` is the row `| **stamp** | ... |`; code font and bold do not count). The stamp then covers that part only. An item that cites a whole file goes stale with every edit of the file.
- `Says` restates the part that this unit uses, in at most 200 characters. It MAY be longer for something the unit implements, such as a data model. `Here` gives the consequence for this unit.
- The comment is the **stamp**: a hash of the cited part. Nobody types it, and only `unifold stamp` writes it, printing each item it confirms. The checker warns while a stamp is missing or its source has changed: read the source, correct `Says`, then run `unifold stamp`.
- Cite only what matters here. More than about ten items usually means that the file copies its ancestors instead of selecting from them. Other files of the unit refer to an item by linking to this file.

## The other explanation files

- `requirements.md` states what the unit must achieve and for whom, then its quality goals in the order in which they win when they conflict. Each goal names something a review or a test could observe. "Fast" is not a goal; "a batch of 500 is answered within 200 ms" is. Guarantees of one capability stay in `README.md`.
- `reasoning.md` is the long form of `## Why`. Write one bold sentence per force, then the paragraph that explains it, and link every rejected alternative to its decision. Trade-offs are a table: chosen, given up, decision.
- `invariants.md` is a list. Each line is a statement that is true at every moment, or never, and names where it holds.
- `runtime.md` says how one unit behaves while it runs: its states and the transitions between them, what happens at start and at stop, timing and timeouts, concurrency, limits, and what it does when something fails. In words, tables and state diagrams. The state tables a unit's code needs go here. A story that walks through several units in order is a scenario in the manifest, where it is checked and drawn; a hand-drawn sequence diagram of such a story is a review finding.
- `deployment.md` is a table: part, where it runs, instances, durable state, reachable from outside. Below it, the consequences: what can be restarted, what is a single point of failure.
- `risks.md` lists risks, known limits and technical debt, one bold label each, with what it costs and what would remove it. A decision that was taken knowingly is cited, not repeated.

## Decisions

Decision records use [MADR](https://adr.github.io/madr/): one file per decision, `docs/decisions/NNNN-short-title.md`, with a four-digit number that is unique within the unit, and this front matter:

```yaml
---
status: proposed      # or: accepted, rejected, deprecated, superseded by NNNN, derived
date: 2026-10-07
decision-makers: [name]   # once the status is accepted
---
```

- A decision belongs to the lowest unit whose insides it fully covers. A decision about how two siblings talk belongs to their parent.
- **Agents propose, humans accept.** An agent writes `status: proposed`. Only a person who may decide for the unit sets `accepted`.
- A decision that a source makes, not a person and not an agent, has `status: derived` and `derived-from`, the passage, and a section `## Source says` that summarises the passage in the author's words, complete enough that the decision stands alone without the source. An agent may write it. It binds like `accepted` until a person accepts or supersedes it. Whether the passage says what the decision claims is a review question, as `Says` is.
- Only accepted and derived decisions bind. Tools mark proposed ones where they show them.
- An accepted decision is not edited, except for its status and for links to files that moved. To replace it, write a new one and set the old one to `superseded by NNNN`. To change only a part, write a new one that says "This amends NNNN:" and what changes; the rest of the old one stays in force.
- `docs/decisions/index.md` is generated for each unit that has decisions.

## References and the glossary

A reference is `docs/references/<topic>.md`: facts in the present tense, for example the contract of a capability, a wire format or a convention. Reasons go to decisions, procedures to skills. A reference that would exceed the line limit becomes a folder with an `index.md` that links to every part. API reference that a tool produces from code is not written by hand. `docs/references/glossary.md` holds the terms that have one fixed meaning inside the unit, one table row per term, so that each can be cited alone. A term is defined in the lowest unit that covers its uses.

`docs/references/constants.md` holds the fixed values a unit and the units below it use: a table whose first columns are `Name` and `Value`, one row per value, named everywhere else and written out only there. Its front matter MAY set `name-pattern`, a regular expression for the names; the default matches capitals in at least two words, `MAX_PAYLOAD`. Where such a table exists, every name of that form in a code span of a hand-written document of the unit or a unit below it is a row of the nearest table or of a table above it.

## Contracts

A contract is the one document of a connection: both sides name it, the consumer's tests are written from it, and the fake that stands in for it in those tests is defined in it. [contracts.md](contracts.md) explains it and holds the template. Its body:

- A header that says whose contract it is, `Notation:`, the notation of the signature blocks, and `Sources:`, a line of text that says where the facts come from. WIT, the interface language of the WebAssembly component model, is the default notation; any other is allowed, and there is no list.
- `## Parts` holds one `###` heading per part. The heading is the part's name, lower-case kebab-case, the same name the manifests use under `parts`.
- `Kind:` is `command`, `query`, `event` or `type`.
- Every part has a fenced code block: its signature. The checker verifies that the block exists and reads nothing inside it.
- A command or query has `Pre:`, `Result:`, `Errors:` and an `Examples:` table with at least one row. Examples are inputs with expected results; they are the first tests of the provider and the whole behaviour of a replay fake.
- A type is defined once within the subtree of the unit that holds the contract. Another contract that uses it links to the definition.
- `## Fake` says what a stand-in for this contract does in the tests of its consumers: it replays the examples and refuses everything else, or it shows a strongly simplified behaviour that the section describes, with the faults it can inject. For a contract whose provider is a `logic` unit the section MAY say `the real implementation`.
- A contract that outgrows the line limit becomes a folder: `index.md` holds the header and `## Parts` as a list of links, and every part is a file `<part>.md` with the same body as a `###` section. A part name resolves to a heading in the contract file or to a file in the contract folder.

## Skills

A skill is a how-to guide for a recurring task in the unit, in the [Agent Skills](https://agentskills.io/specification) format: `docs/skills/<name>/SKILL.md`, with a front matter that has `name`, equal to the folder name, and `description`. The description says for whom the procedure is, when it is written for an end user.

- A skill belongs to the lowest unit in which the whole procedure happens. The generated `AGENTS.md` lists every skill of the unit.
- `unifold skills sync` writes a generated stub for each skill where agents search for skills ([agents.md](agents.md)). The source stays here.
- A person reviews a skill that an agent wrote before others rely on it.

## Tutorials

A tutorial is `docs/tutorials/<name>.md`: a lesson that leads one stated reader, for example "a developer who has cloned the repository" or "an owner with a new sensor stick", through numbered steps to one result they can see. It uses one concrete example throughout, says at each step what the reader should now observe, and explains nothing that is not needed to take the next step. What a thing is belongs in a reference; why it is so in an explanation; both are linked, not repeated. A tutorial is tried by a person before others rely on it.

## Review checklist

The checker compares files with each other. Whoever reviews a change, a person or an agent, checks the meaning:

1. Can the unit be used after reading its `README.md` and the contracts that its manifest names? Does a section of `README.md` repeat what a contract says?
2. Does a file name a sibling, a user or, outside `context.md`, an ancestor? Write the need or capability it stands for instead.
3. Does the parent restate what a child provides or how it works inside?
4. Does `## Why` or an explanation file list units or connections? Does a hand-drawn sequence diagram tell a story that a scenario tells?
5. For each changed connection: does the provider cover what the need expects? `unifold capability` prints both sides. Do the examples of each part cover its errors and the sides of every precondition?
6. Is each `Says` still true to its source, and each `Here` still true? Does the passage a `derived` decision cites say what `## Source says` claims?
7. Is a changed value or limit stated elsewhere? Search for the old value.
8. Did anything set a decision to `accepted` without a person asking for it?
9. Does `status` match reality, and does `contract` point at what really defines the capability? Does the `responsibility` join unrelated things with "and"?
10. Does each guarantee and each goal name something a test could observe?
11. Is every file of its kind: does a reference give reasons, a tutorial define, an explanation instruct? Move the passage to its home.

## Markdown style

- A hand-written file has at most 200 lines (`max-lines` in the root manifest). Before one grows beyond that, split the reference, or move the long why to `docs/explanation/reasoning.md` or a procedure into a skill. Or ask whether the unit is too big. Write one line per paragraph and per list item; nobody wraps prose by hand.
- A mention of another file SHOULD be a link whose text says what the target is. Units, capabilities and needs are named in code font. A file has one `#` title; `##` and `###` follow without skipping a level.
- State facts in the present tense, the main statement first. Name the actor: "the gateway rejects uploads above 1 MB". No history; that is in the decisions and in version control.
- A sentence makes one statement and SHOULD have at most 25 words; in a step of a skill or a tutorial, at most 20. Split at the colon or semicolon that joins two statements. A paragraph has one topic and at most six sentences; a list item is a paragraph.
- A step is an instruction: the verb first, one action per sentence, then what the reader sees. "Run `check`. It prints no error." Not: "After running `check`, which should print no error, ...".
- One term for one thing: the term of [spec.md](spec.md) section 1 or of the unit's glossary, never a synonym. A unit *provides* and *needs*; the parent *connects*. Not "offers" or "exposes" for provides, not "depends on" for needs.
- YAML in a manifest is written in block style, one key per line; the short form `name: one-line summary` for a capability or need stays. Flow style, `{...}`, is valid and the checker does not care, but a value that contains `:` or a comma must then be quoted.

What the reference tool reports is in [rules.md](rules.md).
