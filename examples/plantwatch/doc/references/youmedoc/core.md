# The core of youmedoc

The core is the part of youmedoc that can be followed with a text editor and
without copying anything into the repository. A project that follows only the
core says so in its root manifest with `level: core`. The other chapters build
on these rules and never contradict them.

## The rules

1. **Unit.** A unit is a folder that contains a manifest `unit.yaml` and a
   `README.md`. Every other folder is a plain folder. Being a unit is optional.
2. **Root.** The top folder of the project is a unit. Its manifest has the key
   `youmedoc` with the version of this standard, here `"0.1"`.
3. **Manifest.** A manifest has `unit`, which equals the folder name, and a
   one-line `summary`. It may have `status`: `planned`, `active` (the default)
   or `deprecated`.
4. **Ports.** The manifest lists what the unit `provides` and what it `needs`.
   Each entry has a name and a one-line `summary`. A need says what is needed.
   It never says who has it.
5. **README.** The `README.md` describes the unit as a closed box: what each
   provided port guarantees and what each need expects. It can be understood
   without opening another file, and it does not name the units around it.
6. **Parent.** The parent of a unit is the nearest unit above it in the folder
   tree. Plain folders in between do not count.
7. **Wiring.** The manifest of the parent connects ports in `wiring`. The key
   is the need, the value is the provider:
   - `child.need: other-child.port` meets a child's need with a sibling's port,
   - `child.need: own-need` passes a child's need up to the parent's own need,
   - `own-port: child.port` lets a child implement a port of the parent.
8. **One level.** Wiring names only the unit's own ports and the ports of its
   direct children. Nothing reaches into a grandchild.
9. **Complete.** Every need of every child is wired, unless the need says
   `optional: true`. The needs of the root unit are what the project requires
   from the outside world.
10. **Generated.** Diagrams of units and their connections are generated from
    the manifests and are never drawn by hand.

## Example

```yaml
# storage/unit.yaml
unit: storage
summary: Durable key-value storage with a write-ahead log
provides:
  kv-api: {summary: Read and write keys in transactions}
needs:
  clock: {summary: A monotonic time source}
```

```yaml
# unit.yaml of the parent
unit: app
youmedoc: "0.1"
level: core
summary: An example application
provides:
  http-api: {summary: The public API}
wiring:
  http-api: api.http-api
  api.store: storage.kv-api
  storage.clock: platform.time-api
```

## What you get

- Every folder that matters says what it offers and what it depends on.
- A missing provider, an unused port and a dependency cycle are found by a
  tool before code exists ([rules-tool.md](rules-tool.md), rules `S1` to
  `S4`, `M`, `W` and `G`).
- Three diagrams per unit, generated ([diagrams.md](diagrams.md)), and one
  command that tells who provides each need and who uses each port
  ([checker.md](checker.md)).

## What the core leaves out

| Not in the core | Chapter |
|---|---|
| `AGENTS.md` per unit, with the reasons and pointers for agents | [unit-files.md](unit-files.md) |
| The `doc/` folder: inherited context, decisions, references, skills | [doc-folder.md](doc-folder.md) |
| Where a file may link to, and the limit of 200 lines | [rules.md](rules.md), [markdown.md](markdown.md) |
| A copy of the standard and its skills in the repository | [index.md](index.md) |
| The review rules | [rules-review.md](rules-review.md) |

A project starts at the core and moves to the full standard by removing
`level: core` and running `youmedoc init` ([workflow.md](workflow.md)).

## Details the core relies on

The exact fields of the manifest, including optional ones such as `kind`,
`contract` and named alternatives, are in [manifest.md](manifest.md) and
[wiring.md](wiring.md). A manifest may also be the front matter of the
`README.md` instead of a file.
