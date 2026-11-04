# Decisions and context items

How a decision record is written, and how a unit takes over a decision, a convention or a term from the units above it. [writing.md](writing.md) says how the other documents are written.

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
- A decision that a source makes, not a person and not an agent, has `status: derived` and `derived-from`, the passage, and a section `## Source says` that summarises the passage in the author's words, complete enough that the decision stands alone without the source. An agent may write it. It binds like `accepted` until a person accepts or supersedes it. Whether the passage says what the decision claims is a review question.
- Only accepted and derived decisions bind. Tools mark proposed ones where they show them.
- An accepted decision is not edited, except for its status and for links to files that moved. To change it, write a new decision and set the old one to `superseded by NNNN`.
- The change that a decision makes rewrites the documents it touches to the new state, in the same change.
- A unit below that depends on a decision takes it into its `context.md`, and its documents state the result. A decision of another unit may also be named by the unit and the number: `transport/0002`.
- `docs/decisions/index.md` is generated for each unit that has decisions.

## Context items

`docs/explanation/context.md` lists the decisions, conventions and terms from above that a reader must know to understand the unit. Each item is a `###` heading that links to its source, followed by what it means for this unit:

```markdown
### [cloud/0002 Each service owns its data](../../../docs/decisions/0002-each-service-owns-its-data.md)

No service reads or writes the database schema of another, so `ingest` keeps its duplicate index in a schema of its own.
```

- Link the smallest part that applies: one section (`#heading`) or, where no heading has that anchor, one table row whose first cell gives it (`glossary.md#unit` is the row `| **unit** | ... |`; code font and bold do not count).
- Cite only what matters here. More than about ten items usually means that the file copies its ancestors instead of selecting from them. Other files of the unit refer to an item by linking to this file.
- When a source changes, `unifold impact FILE` lists the context items that link it. Read each again.
