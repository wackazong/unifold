---
status: proposed
date: 2026-10-24
---

# Define well-known kinds for units and for capabilities and needs

## Context and Problem Statement

`kind` is free text, on a unit and on each capability and need. Rule `W4` reports a need and a provider whose kinds differ. Free text makes the rule weak in both directions: `library` against `lib` gives a warning that is only a spelling, and a side that has a misspelt kind and a partner with none gives nothing.

Nothing can interpret a kind either. The exporters of [0059](0059-export-the-map-to-structurizr-backstage-and-graphviz.md) have to decide which units are systems, containers or components. The two examples of this repository use 18 values, and unit kinds and connection kinds share some words: `adapter`, `app`, `cli`, `db`, `events`, `file`, `firmware`, `hardware`, `http`, `infrastructure`, `library`, `protocol`, `queue`, `service`, `system`, `test`, `tool`, `ui`.

## Considered Options

- Keep free text
- A closed list; any other value is an error
- Two lists of well-known kinds with their meanings; any other value starts with `x-`, or is reported as a warning

## Decision Outcome

Chosen option: "two lists, and `x-` for the rest", because a kind has to mean the same in every project before a tool can use it, and a project still needs room for kinds that the lists do not know.

Kinds of a unit:

| Kind | Meaning |
|---|---|
| `system` | A unit whose children together make a product or a part of one |
| `service` | A process that serves others over a network |
| `app` | A program for end users: mobile, desktop, web front end, command |
| `firmware` | A program that runs on a device |
| `tool` | A program for developers, such as an emulator or a generator |
| `test` | A rig or a suite that runs other units |
| `library` | Code that other units link or import |
| `adapter` | A unit that needs one kind and provides another |

Kinds of a capability or need:

| Kind | Meaning |
|---|---|
| `library` | Code that is linked or imported at build time |
| `cli` | A command that is run as a process |
| `http` | Requests and responses over HTTP |
| `rpc` | Remote procedure calls, such as gRPC |
| `events` | Messages that are published to subscribers |
| `queue` | A broker that stores and delivers messages |
| `db` | A database in which the unit keeps data |
| `file` | A file or folder that one side writes and the other reads |
| `protocol` | A wire protocol that is not HTTP or RPC, such as a radio or serial link |
| `hardware` | A device, a sensor or a bus |
| `infrastructure` | A platform that runs or stores, such as a container host |
| `ui` | A user interface |

- A kind that is neither well known nor starts with `x-` gives the new warning `M11`. Its fix names the nearest well-known kind.
- `W4` does not change. It compares a need and its provider when both state a kind.
- The two lists are in [spec.md](../references/spec.md) section 2, which stays below 200 lines. The schema of the manifest lists them as an enumeration with the pattern `^x-`.
- The lists change only by a decision. A kind joins when two projects use it with one meaning.
- The examples change `kind` where they use none of these values.

### Consequences

- Good: a kind means the same in every project, so checks and exports can use it.
- Good: a misspelt kind is found on its own side, without a partner.
- Bad: no list fits every project. Some projects will write many `x-` kinds.
- Bad: existing projects get warnings until they rename their kinds.
- Bad: the lists invite debates about where a part belongs, such as whether a web front end is an `app` or a `ui`.
