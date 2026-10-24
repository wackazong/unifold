# Rules of the reference tool

`unifold check` applies these rules, and each finding names one of them. The [standard](spec.md) says what a checker must report; this chapter says how the reference tool reports it. What no tool can check is in the [review checklist](writing.md#review-checklist).

## Reading a finding

```text
error W2 cloud/unifold.yaml:14: need 'alerts.push' has no provider
    fix: Add `alerts.push: <provider>` to the wiring of this manifest, or declare a need `push` here to pass it up.
```

The parts are: severity, rule, the file to change with the line, what is wrong, and how to fix it. `unifold rules W2` prints one rule. `check --json` gives the same as data ([tool-json.md](tool-json.md)).

| Severity | Meaning | Effect on `check` |
|---|---|---|
| `error` | The map is inconsistent. | Exit code 1. |
| `warn` | Probably a mistake, or work that is left. A person decides. | Exit code 1 only with `--strict`. |
| `info` | A fact worth knowing. | None. Hidden by `--quiet`. |

No finding means consistent, not correct: the tool does not judge whether a summary or a restatement is true.

## S: structure

| Rule | Severity | What must hold | How to fix |
|---|---|---|---|
| <a id="s1"></a>`S1` | error | The root manifest states a version of the standard that this tool supports, as a string. | Write `unifold: "0.2"` in the root `unifold.yaml`. |
| <a id="s3"></a>`S3` | error | Every unit has a `README.md`. | Write the file (the template is in the `unifold` skill). |
| <a id="s7"></a>`S7` | error | Every folder in `docs/skills/` has a `SKILL.md` whose front matter has `name`, equal to the folder name, and `description`. | Correct the front matter. |
| <a id="s9"></a>`S9` | error | A decision file is named `NNNN-short-title.md` with a number that is unique in the unit; its front matter has a valid `status` and an ISO `date`; `accepted` names `decision-makers`; `superseded by NNNN` names an existing decision. | Correct the file name or the front matter. |
| <a id="s12"></a>`S12` | info | Every entry directly in `docs/` is one of `tutorials`, `skills`, `references`, `explanation`, `decisions`, `diagrams`. | Move the file or folder into the folder of its kind: tutorials (learn), skills (do), references (look up), explanation (understand). |

## M: manifest

| Rule | Severity | What must hold | How to fix |
|---|---|---|---|
| <a id="m1"></a>`M1` | error | A manifest is a YAML mapping without duplicate keys. | Correct the YAML. The unit and its wiring are not checked until it parses. |
| <a id="m2"></a>`M2` | error | A manifest has a one-line `summary` and otherwise only the keys, types and values of the standard; root-only keys are in the root; names of capabilities and needs use letters, digits, `-` and `_` and start with a letter or digit; no summary is a placeholder (`<...>`). | Correct the key or value named in the message. Project-specific keys start with `x-`. |
| <a id="m7"></a>`M7` | error | `contract` is a path, relative to the manifest, to a Markdown file that exists in `docs/references/` of this unit or of an ancestor. `verified-by` is a URL or a path, relative to the manifest, that exists and lies in this unit, an ancestor or a descendant. | Write the contract as `docs/references/<topic>.md` of the unit that wires the connection, and name it from both sides. A schema file is not a contract, and a definition from outside the project is linked from the reference by its URL. Otherwise correct the path, create the file, or remove the key until there is something to point at. |
| <a id="m10"></a>`M10` | warn | No summary is still `TODO`. | Replace `TODO` with one line that says what the unit, capability or need is. |

## W: wiring

A finding about wiring names the manifest that holds the line: the parent's for a need of a child, the unit's own for a need it meets inside.

| Rule | Severity | What must hold | How to fix |
|---|---|---|---|
| <a id="w1"></a>`W1` | error | Every wiring line has an allowed form and names an existing direct child, capability or need, on the correct side. A bare key names a capability or a need of the unit, not both. A need of a child is passed up only to a need that the unit does not meet inside, and a need that a child meets inside is not wired again. A connection joins two units; a folder is never a provider. | Correct the reference. `unifold show` lists the names; where two children share a folder name, write the path (`a/utils.matcher`). Code that is not a unit gets a folder with a `unifold.yaml`. |
| <a id="w2"></a>`W2` | error | Every need of every child is connected by a line in the parent's wiring, unless it is `optional` or the child meets it inside. | Add `child.need: provider` to the parent's wiring, for a capability of a sibling, or declare a need in the parent and pass the need up (`child.need: need`). Do not mark a need optional to silence this. |
| <a id="w3"></a>`W3` | warn | Every capability of a child is used: a wiring line names it as the provider of a need of a sibling or of the parent itself, or a capability of the parent is implemented by it. | Wire the unit that should use it; where code of the parent itself uses it, declare a need in the parent and wire it (`need: child.capability`); or implement a capability of the parent with it (`capability: child.capability`); or remove the capability. |
| <a id="w4"></a>`W4` | warn | A need and its provider have the same `kind`, if both state one. | Put an adapter unit between the two, or correct the kind that is wrong. |
| <a id="w7"></a>`W7` | warn | The children of a unit do not need each other in a cycle. | Move what both need into a third unit, or turn one direction around (the other side subscribes). |
| <a id="w9"></a>`W9` | warn | An `active` unit does not get a mandatory need from a provider that is `planned` or `deprecated` (default alternative). | Correct the status, or wire a provider that exists. |
| <a id="w11"></a>`W11` | error | Every side of a connection names a contract, and both sides name the same document. | Write the definition as a reference of this unit, the one that holds the wiring, or of a unit above it, and point both sides at it with `contract`. |

## L: links and context items

These rules read the hand-written documents of a unit ([documents.md](documents.md)): `README.md` and the Markdown files in `docs/tutorials/`, `docs/explanation/`, `docs/decisions/`, `docs/references/` and `docs/skills/` (not the `assets/` and `scripts/` of a skill). Links inside code blocks and code spans are ignored.

| Rule | Severity | What must hold | How to fix |
|---|---|---|---|
| <a id="l1"></a>`L1` | error | The target of every relative link in a hand-written document exists, including its anchor: a heading, or the first cell of a table row. | Correct the link. |
| <a id="l2"></a>`L2` | error | A relative link stays inside the project, and no link is an absolute path. | Write the link relative to this file; cite things outside the project by full URL. |
| <a id="l7"></a>`L7` | warn | `docs/explanation/context.md` cites no decision that is rejected, deprecated or superseded, and an `active` unit cites no decision that is still `proposed`. | Cite the successor, or have the decision accepted. |
| <a id="l9"></a>`L9` | warn | Every item of `docs/explanation/context.md` is a `###` heading with a link, followed by a paragraph that starts with `Says` and one that starts with `Here`. | Complete the item. |
| <a id="l10"></a>`L10` | warn | Every context item carries a stamp, and the cited part (the file, or the section or table row that the fragment of the link names) has not changed since the stamp was written. | Read the cited source again, correct `Says`, then run `unifold stamp`. Only `unifold stamp` writes stamps; `check --fix` never does. |
| <a id="l11"></a>`L11` | warn | A link stays inside the unit, goes down to a direct child (its folder or its `README.md`), goes up from `docs/explanation/context.md` to an ancestor's `README.md`, decisions or references, or targets a file that the unit's manifest names as `contract` or `verified-by`. No other link goes sideways or deeper. | Remove the link. What the unit wants from a sibling is a need in its manifest; what it takes from above is an item in `docs/explanation/context.md`. |

## T: text

| Rule | Severity | What must hold | How to fix |
|---|---|---|---|
| <a id="t1"></a>`T1` | warn | A hand-written document has at most `max-lines` lines (default 200). | Split the file: a reference into parts, the long why into `docs/explanation/reasoning.md`, a procedure into a skill. |
| <a id="t4"></a>`T4` | warn | The `## Why` section of `README.md` has at most 20 lines that are not blank. | Move the long form to `docs/explanation/reasoning.md`. |
| <a id="t5"></a>`T5` | warn | A `###` heading in code font under `## Capabilities` or `## Needs` of a `README.md` names a capability or need of the manifest. | Rename or remove the section; the manifest is the list of capabilities and needs. |

## G: generated files

`check` builds every generated file in memory and compares. The generated marker exempts a file from the document rules only at a path that the generator writes.

| Rule | Severity | What must hold | How to fix |
|---|---|---|---|
| <a id="g1"></a>`G1` | error | Every generated file exists, is not ignored by git, and equals what the generator writes now; no leftover generated file remains; `docs/diagrams/` holds only generated files and `AGENTS.md` is generated. | Run `unifold generate` (or `unifold check --fix`). A hand-written `AGENTS.md` is not overwritten: move its content to `README.md` and `docs/`, delete it, then run the command. |

## Order and cascades

- A manifest that does not parse gives one `M1`. The unit keeps its place in the tree, its children keep their parent, and no wiring finding is reported for lines that name it.
- A root manifest that does not parse, or states an unsupported version, gives one `M1` or `S1` and nothing else: the project cannot be read.
- `M1` and `S1` come first in the output; the rest is sorted by file and line.

## Rules of a project

A project MAY add checks of its own in its build. It SHOULD NOT silence a rule of this table by weakening a manifest, for example by marking a need `optional`. Where a rule cannot be followed in one place, say so in a reference of the root unit, so that reviewers see the exception.

## Changes to this table

Rule ids are never reused. The gaps in the numbering are rules that were merged or removed before version 0.1, and `D1` to `D3`, which compared the wiring with dependencies in code until version 0.2.
