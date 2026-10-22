# Writing the documents

[documents.md](documents.md) says which files a unit at level `full` has and
where each kind of knowledge goes. This chapter says how each file is
written, what a reviewer checks, and the style that all of them share.

## Context items and stamps

`docs/explanation/context.md` lists the decisions, conventions and terms
from above that a reader must know to understand the unit. The repetition
is deliberate: it keeps the unit understandable when its folder is read
alone. Each item:

```markdown
### [cloud/0002 Each service owns its data](../../../docs/decisions/0002-each-service-owns-its-data.md)
<!-- unifold:cites sha=3f9a1c2e -->

Says: no service reads or writes the database schema of another.

Here: `ingest` keeps its duplicate index in a schema of its own.
```

- The heading links to the source. **Cite the smallest part**: a fragment
  cites one section (`#heading`) or, where no heading has that anchor, one
  table row whose first cell gives it (`glossary.md#stamp` is the row
  `| **stamp** | ... |`; code font and bold do not count). The stamp then
  covers that part only. An item that cites a whole file goes stale with
  every edit of the file.
- `Says` restates the part that this unit uses, in at most 200 characters.
  It MAY be longer for something the unit implements, such as a data model.
  `Here` gives the consequence for this unit.
- The comment is the **stamp**: a hash of the cited part. Nobody types it,
  and only `unifold stamp` writes it, printing each item it confirms. The
  checker warns while a stamp is missing or its source has changed: read
  the source, correct `Says`, then run `unifold stamp`.
- Cite only what matters here. More than about ten items usually means that
  the file copies its ancestors instead of selecting from them. Other files
  of the unit refer to an item by linking to this file.

## The other explanation files

- `requirements.md` states what the unit must achieve and for whom, then
  its quality goals in the order in which they win when they conflict.
  Each goal names something a review or a test could observe. "Fast" is
  not a goal; "a batch of 500 is answered within 200 ms" is. Guarantees of
  one capability stay in `README.md`.
- `reasoning.md` is the long form of `## Why`. Write one bold sentence per
  force, then the paragraph that explains it, and link every rejected
  alternative to its decision. Trade-offs are a table: chosen, given up,
  decision.
- `invariants.md` is a list. Each line is a statement that is true at every
  moment, or never, and names where it holds.
- `runtime.md` holds the scenarios that cross several parts and therefore
  cannot be told by one of them: a sequence, a state machine, the order of
  a start. Mermaid, drawn by hand, each with one sentence that says what it
  shows and which parts appear.
- `deployment.md` is a table: part, where it runs, instances, durable
  state, reachable from outside. Below it, the consequences: what can be
  restarted, what is a single point of failure.
- `risks.md` lists risks, known limits and technical debt, one bold label
  each, with what it costs and what would remove it. A decision that was
  taken knowingly is cited, not repeated.

## Decisions

Decision records use [MADR](https://adr.github.io/madr/): one file per
decision, `docs/decisions/NNNN-short-title.md`, with a four-digit number
that is unique within the unit, and this front matter:

```yaml
---
status: proposed      # or: accepted, rejected, deprecated, superseded by NNNN
date: 2026-10-07
decision-makers: [name]   # once the status is accepted
---
```

- A decision belongs to the lowest unit whose insides it fully covers. A
  decision about how two siblings talk belongs to their parent.
- **Agents propose, humans accept.** An agent writes `status: proposed`.
  Only a person who may decide for the unit sets `accepted`.
- Only accepted decisions bind. Tools mark proposed ones where they show them.
- An accepted decision is not edited, except for its status. To change it,
  write a new one and set the old one to `superseded by NNNN`.
- `docs/decisions/index.md` is generated for each unit that has decisions.

## References and the glossary

A reference is `docs/references/<topic>.md`: facts in the present tense,
for example the contract of a capability, a wire format or a convention.
Reasons go to decisions, procedures to skills. A reference that would
exceed the line limit becomes a folder with an `index.md` that links to
every part. A contract SHOULD contain examples: inputs with expected
results. API reference that a tool produces from code is not written by
hand. `docs/references/glossary.md` holds the terms that have one fixed
meaning inside the unit, one table row per term, so that each can be cited
alone. A term is defined in the lowest unit that covers its uses.

## Skills

A skill is a how-to guide for a recurring task in the unit, in the
[Agent Skills](https://agentskills.io/specification) format:
`docs/skills/<name>/SKILL.md`, with a front matter that has `name`, equal to
the folder name, and `description`. The description says for whom the
procedure is, when it is written for an end user.

- A skill belongs to the lowest unit in which the whole procedure happens.
  The generated `AGENTS.md` lists every skill of the unit.
- `unifold skills sync` writes a generated stub for each skill where agents
  search for skills ([agents.md](agents.md)). The source stays here.
- A person reviews a skill that an agent wrote before others rely on it.

## Tutorials

A tutorial is `docs/tutorials/<name>.md`: a lesson that leads one stated
reader, for example "a developer who has cloned the repository" or "an
owner with a new sensor stick", through numbered steps to one result they
can see. It uses one concrete example throughout, says at each step what
the reader should now observe, and explains nothing that is not needed to
take the next step. What a thing is belongs in a reference; why it is so
in an explanation; both are linked, not repeated. A tutorial is tried by a
person before others rely on it.

## Review checklist

The checker compares files with each other. Whoever reviews a change, a
person or an agent, checks the meaning:

1. Can the unit be used after reading only its `README.md`?
2. Does a file name a sibling, a user or, outside `context.md`, an
   ancestor? Write the need or capability it stands for instead.
3. Does the parent restate what a child provides or how it works inside?
4. Does `## Why` or an explanation file list units or connections?
5. For each changed connection: does the provider cover what the need
   expects? `unifold capability` prints both sides.
6. Is each `Says` still true to its source, and each `Here` still true?
7. Is a changed value or limit stated elsewhere? Search for the old value.
8. Did anything set a decision to `accepted` without a person asking for it?
9. Does `status` match reality, and do `contract` and `verified-by` point
   at what really defines and checks the capability?
10. Does each guarantee and each goal name something a test could observe?
11. Is every file of its kind: does a reference give reasons, a tutorial
    define, an explanation instruct? Move the passage to its home.

## Markdown style

- A hand-written file has at most 200 lines (`max-lines` in the root
  manifest). Before one grows beyond that, split the reference, move the
  long why to `docs/explanation/reasoning.md` or a procedure into a skill,
  or ask whether the unit is too big. Wrap prose at about 80 characters.
- A mention of another file SHOULD be a link whose text says what the
  target is. Units, capabilities and needs are named in code font. A file
  has one `#` title; `##` and `###` follow without skipping a level.
- State facts in the present tense, the main statement first. Name the
  actor: "the gateway rejects uploads above 1 MB". No history; that is in
  the decisions and in version control.
- One term for one thing. One home for every fact; other files link to it.
- What the reference tool reports is in [rules.md](rules.md).
