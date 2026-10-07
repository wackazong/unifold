# The ruleset

The rules make a unifold project checkable. Each rule has an ID, so that a
finding can be reported and fixed precisely.

## Two sorts of rules

| Sort | Checked by | Defined in | IDs |
|---|---|---|---|
| Tool rules | The [checker](checker.md), mechanically | [rules-tool.md](rules-tool.md) | `S`, `M`, `W`, `L`, `T`, `G`, `D` |
| Review rules | An agent or a human, by reading | [rules-review.md](rules-review.md) | `C1` to `C15` |

Tool rules compare files with each other. Review rules concern meaning: is
the text true, is it in the right place, does it say too much.

A project without findings from the tool is consistent. It is not thereby
correct: the tool does not read prose for meaning and does not read code. The
checker says so in its last line.

## Severity

| Letter | Meaning | Effect |
|---|---|---|
| `E` | Error | The project does not conform. Fix it before the change is accepted. |
| `W` | Warning | Probably a mistake. A human decides. |
| `I` | Info | A fact worth knowing. No action required. |

Review rules have no severity. A broken review rule is an error.

## How to enforce the ruleset

An agent that is asked to check a project, or that has changed one, uses the
[check-docs](../../skills/check-docs/SKILL.md) skill. In short:

1. Run the generator, then the checker, and fix every error.
2. Look at every warning and either fix it or say why it stands.
3. Go through the review rules that apply to the kind of change.
4. Report what was found, by rule ID and file.

## The reference-direction rules

These rules say what a file of a unit may refer to. They implement the
principle that knowledge points inward and downward
([concepts.md](concepts.md)). They apply to hand-written files. Generated
files are exempt. "Refer to" covers both links and mentions by name.

| From a file of unit U | To | Allowed | Not allowed |
|---|---|---|---|
| any file | U's own files, and files in plain folders of U | everything | |
| any file | a direct child of U | the child's name and its `README.md`; a general pointer such as "follow that unit's own skills" | links into the child's `AGENTS.md`, `doc/` or code; restating the child's interface or insides |
| any file | a unit deeper than a child | nothing | any link or mention; go through the child |
| `doc/context.md` | an ancestor of U | its `README.md`, files in its `doc/decisions/` and `doc/references/`, each with a restatement | its `AGENTS.md`, `doc/architecture.md`, skills, diagrams, code |
| any other file | an ancestor of U | nothing | any link or mention |
| any file | a sibling of U, or anything else in the project | nothing; what U wants from it is a need in the manifest | any link or mention |
| manifest `wiring` | ports | own ports, ports of direct children, plain folders of U | ports of deeper units |
| manifest `contract`, `verified-by` | files | paths inside U, or URLs | paths outside U |
| any file | the outside world | full URLs | |
| any file below the root | the standard and its three skills | their names, or the URL of the published standard | relative links to the root's copy |
| a nested project's parent unit | the nested project | its `README.md` | anything else in it |

Which rule covers which row:

| Row | Tool rule | Review rule |
|---|---|---|
| Links down | `L2` | `C3` for mentions and restatements |
| Links up | `L3`, `L7`, `L8` | `C2` for mentions, `C5` for the restatement |
| Links sideways or out of the project | `L4` | `C2` for mentions |
| Names of siblings and ancestors | `L6`, when written in code font | `C2` |
| Wiring endpoints | `W1` | `C13` for whether both ends match |
| Contract and verification paths | `M7` | `C15` |

### Why these directions

- **Down only to the interface.** If a parent described the insides of a
  child, every change inside the child would force a change in the parent,
  and the parent would grow with the size of the tree.
- **Up only through one file.** A unit depends on decisions made above it.
  Collecting these references in `doc/context.md` shows at a glance what the
  unit inherits, and it leaves one file to repair after the unit is moved or
  copied.
- **Never sideways.** A unit that names a sibling can no longer be understood
  or reused without it. Stating the need instead keeps the unit independent of
  who provides it. This is dependency inversion applied to documents
  ([principles.md](principles.md)).

A unit can still find out who is on the other side of its ports: the
generated `doc/diagrams/context.md` lists its resolved neighbours
([diagrams.md](diagrams.md)).

## After a unit is moved or copied

The links in `doc/context.md` break, and `L1` reports each of them. That is
intended: the list of errors is the list of inherited items to re-establish in
the new place. See [workflow.md](workflow.md).

## Project rules and deviations

A project MAY add rules of its own. It records them in a reference of the
root unit and gives them IDs that start with `X`.

A project MUST NOT silently switch off a rule of the standard. Where a rule
cannot be followed in one place, the project records the deviation in a
reference of the root unit named `deviations.md`: which rule, where, and why.
A recorded deviation is visible to reviewers. A warning that everybody
ignores is not.
