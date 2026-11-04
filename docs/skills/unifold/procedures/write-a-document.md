# Write a document

Start every file from its template:

| File | Template |
|---|---|
| `unifold.yaml` | [unifold.template.yaml](../assets/unifold.template.yaml) |
| `README.md` of a unit | [README.template.md](../assets/README.template.md) |
| `docs/explanation/<file>.md` | [assets/explanation/](../assets/explanation/): one template per file, `context.template.md` among them |
| `docs/tutorials/<name>.md` | [tutorial.template.md](../assets/tutorial.template.md) |
| `docs/decisions/NNNN-title.md` | [decision.template.md](../assets/decision.template.md); a decision a source makes: [decision-derived.template.md](../assets/decision-derived.template.md) |
| `docs/references/<topic>.md` | [reference.template.md](../assets/reference.template.md); a contract: [write-a-contract.md](write-a-contract.md) |
| `docs/references/constants.md` | [constants.template.md](../assets/constants.template.md) |
| `docs/references/glossary.md` | [glossary.template.md](../assets/glossary.template.md): one row per term |
| `docs/skills/<name>/SKILL.md` | [add-a-skill.md](add-a-skill.md) |
| A section for `CONTRIBUTING.md` | [CONTRIBUTING.snippet.md](../assets/CONTRIBUTING.snippet.md) |

Write every document in language that a human reader understands easily. The rules for each kind of document: <https://unifold.md/writing>.

- In a reference, state the fact and give no reasons. Where a decision settled it, link the decision.
- Describe the unit as it is now. Do not say what changed, when, or which decision changed it; rewrite the sentence to the new fact. The history is in the decisions and in version control.
- Describe what the unit does and needs, not how far it is built. An open question is a proposed decision, and a unit without code has `status: planned`.
- In `## Why`, give reasons. Do not list decisions.
- A document has at most 1,500 words, and `## Why` at most 250. Split a file before it grows beyond that.
