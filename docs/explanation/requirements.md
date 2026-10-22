# Requirements of unifold

What the standard must achieve, for whom it is, and which qualities win
when they conflict. A unit of a project states the same for itself in its
own `docs/explanation/requirements.md`; this file is about the standard.

## Goals

1. **Explainable in one minute.** A reader who knows what a folder and a
   dependency are understands the idea from the first page: a manifest per
   folder, needs that do not name their provider, wiring by the parent, a
   check, generated diagrams.
2. **Adoptable in five.** A repository gets a root manifest and a green
   check in minutes, and every further unit is one small file. Nothing is
   restructured and nothing is copied in.
3. **One set of documents for people and agents.** Whoever opens a folder,
   a newcomer, a maintainer, an end user or a coding agent, finds the same
   files in the same places and reads the same text. Nothing is written
   twice for a second audience, and nothing is kept outside the tree.
4. **Checked, not promised.** Everything the standard asks for is either
   checked by a tool or stated as a question for a reviewer. A clean check
   means that the files agree with each other and with the code.
5. **The standard obeys itself.** Every rule is tried on this repository
   before a project has to follow it.

## Quality goals, in the order in which they win

| Rank | Quality | Observed as |
|---|---|---|
| 1 | Small normative surface | Everything normative for level `core` fits one page of at most 200 lines. |
| 2 | Checkable | Every finding of the tool has an id, a test case and a fix text. |
| 3 | Incremental | One folder can be a unit, and one unit can be at level `full`, while the rest of the repository is untouched and the check stays green. |
| 4 | Independent | No rule depends on a programming language, a build system or a code host. The extractors are features of the tool. |
| 5 | Useful to agents | An agent finds the unit of a file, its interfaces and its documents with one command, and reads only what its task needs. |

## For which repositories

| Shape of the repository | Fit |
|---|---|
| Workspace of packages (Cargo, npm, pnpm, yarn, Go, uv) | Good. The build files name the packages, and `check` compares the wiring with them. |
| Services in one repository | Good. Calls between services need a list of observed dependencies ([wiring](wiring.md)). |
| Firmware or a product of several components | Good: drivers, emulators and applications have real interfaces and stand-ins. |
| Application with feature folders, modular mobile app | Fits with one unit per feature or module. |
| Framework application organised by layer (`models/`, `views/`) | Not on the layer folders. Units belong on the level of features: Django apps, Rails engines. |
| Infrastructure modules (Terraform) | Partly. Modules map to units; environments have no place. |
| Single package or library | A project of one unit. The map is one box; the value is the root at level `full`, whose `README.md` and `docs/` hold everything a reader needs in fixed places. |
| Data pipelines, notebooks | No. The parts are files, and the pipeline tool already has the graph. |
| System spread over several repositories | Each repository is a project of its own. The map across repositories is not produced. |

If the folder layout does not match the architecture, unifold describes the
layout. It does not ask you to restructure code.

## Where the value is

A map with one capability per package restates the build files. The map
becomes worth having with what the build files do not know:

1. Complete summaries, one line each.
2. The outside world: what the project needs from external systems as
   needs of the root, and what it offers as capabilities of the root.
3. Needs named as roles, `matcher` instead of the provider's package name
   ([wiring](wiring.md)).
4. Capabilities split where users depend on different parts of a package,
   with a `contract` and a `verified-by` where a file defines them and
   tests check them.
5. Units for parts that are not packages: the modules of one large
   package, a deployment folder, a shared schema.
6. At level `full`: the why of every unit, and its documents sorted by
   what the reader is doing.

## Design before code

unifold also works before any code exists: write the manifests of the
planned parts with `status: planned`, wire them, and read the generated
diagram as the design. A need that no part can meet shows a missing part.
Do not describe three levels of planned units before the first one runs;
take one thin path through the system to `active` first.
[examples/plantwatch](../../examples/plantwatch/README.md) is such a design.
