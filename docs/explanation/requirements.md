# Requirements of unifold

What the standard must achieve, for whom, and which qualities win when they conflict.

## Goals

1. **Explainable in one minute.** A reader who knows what a folder and a dependency are understands the idea from the first page: a manifest per folder, needs that do not name their provider, wiring by the parent, a check, generated diagrams.
2. **Adoptable in five.** A repository gets a root manifest and a green check in minutes, and every further unit is one small file. Nothing is restructured and nothing is copied in.
3. **One set of documents for people and agents.** Whoever opens a folder, a newcomer, a maintainer, an end user or a coding agent, finds the same files in the same places and reads the same text. Nothing is written twice for a second audience, and nothing is kept outside the tree.
4. **Checked, not promised.** Everything the standard asks for is either checked by a tool or stated as a question for a reviewer. A clean check means that the files agree with each other. Whether the code follows them is for tests and review.
5. **The standard is tried.** Every rule is tried on the examples in this repository before a project has to follow it.

## Quality goals, in the order in which they win

| Rank | Quality | Observed as |
|---|---|---|
| 1 | Small normative surface | Everything normative about manifests, wiring and generated files fits one page of at most 200 lines. |
| 2 | Checkable | Every finding of the tool has an id, a test case and a fix text. |
| 3 | Incremental | One folder can be a unit while the rest of the repository is untouched and the check stays green. |
| 4 | Independent | No rule depends on a programming language, a build system or a code host. Nothing reads code. |
| 5 | Useful to agents | An agent finds the unit of a file, its interfaces and its documents with one command, and reads only what its task needs. |

## For which repositories

| Shape of the repository | Fit |
|---|---|
| Workspace of packages (Cargo, npm, pnpm, yarn, Go, uv) | Good. The packages are candidates for units; the map adds what the build files do not say. |
| Services in one repository | Good. Each service is a unit, and its calls to other services are needs ([wiring](wiring.md)). |
| Firmware or a product of several components | Good: drivers, emulators and applications have real interfaces and stand-ins. |
| Application with feature folders, modular mobile app | Fits with one unit per feature or module. |
| Framework application organised by layer (`models/`, `views/`) | Not on the layer folders. Units belong on the level of features: Django apps, Rails engines. |
| Infrastructure modules (Terraform) | Partly. Modules map to units; environments have no place. |
| Single package or library | Good. A unit is a folder, not a package, so the package is one unit or one per module folder. With one unit the map is one box; the value is the root's `README.md` and `docs/`, which hold everything a reader needs in fixed places. |
| Data pipelines, notebooks | No. The parts are files, and the pipeline tool already has the graph. |
| System spread over several repositories | Each repository is a project of its own. The map across repositories is not produced. |
| A design before any code | Good. Planned units, wired, give a diagram to review, and a need that no part can meet shows a missing part ([plantwatch](../../examples/plantwatch/README.md)). |

If the folder layout does not match the architecture, unifold describes the layout. It does not ask you to restructure code.
