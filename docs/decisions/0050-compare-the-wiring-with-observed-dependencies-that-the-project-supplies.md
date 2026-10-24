---
status: rejected
date: 2026-10-24
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Compare the wiring with observed dependencies that the project supplies

## Context and Problem Statement

[0047](0047-remove-the-comparison-with-code.md) removed the comparison of the wiring with the code. Since then, a clean check proves that the manifests, the generated files and the links agree with each other. It proves nothing about the code: code that uses another unit without a need, and a wiring line that no code needs any more, pass every check. Drift between a description and the code is the failure that every architecture description suffers, and it is now left to review alone.

0047 gave two reasons. The extractors covered only units that happen to be packages or import folders, so a partial guarantee read as a general one. And the extractors were about 970 lines of knowledge of four ecosystems in a tool that is otherwise free of any language. Both reasons concern where the dependencies come from and how their coverage is shown. Neither concerns the comparison itself, which needs no knowledge of a language ([0019](0019-compare-the-wiring-with-dependencies-observed-in-code.md)).

Build tools and module checkers already list which file or rgo metadata`](https://doc.rust-lang.org/cargo/commands/cargo-metadata.html), [`go list`](https://pkg.go.dev/cmd/go#hdr-List_packages_or_modules), [dependency-cruiser](https://github.com/sverweij/dependency-cruiser), [import-linter](https://github.com/seddonym/import-linter) and [Tach](https://github.com/gauge-sh/tach).

## Considered Options

- Keep 0047: no comparison with code
- Bring the extractors of [0025](0025-compare-with-code-by-default-and-draft-manifests-from-build-files.md) back into the tool
- Read a file of observed dependencies in a format of the standard, report which units it covers, and keep every extractor outside this repository
- The same, with errors instead of warnings

## Decision Outcome

Chosen option: "read a file of observed dependencies, report its coverage, keep extractors outside", because it gives back the comparison for exactly the units that a project can observe, says which those are, and keeps the tool free of any language.

### The file

```json
{"unifold-observed": "1",
 "source": "cargo metadata",
 "covers": ["core", "cli", "plugins/unicode"],
 "uses": [
   {"from": "cli/src/main.rs", "to": "core/src/lib.rs"},
   {"from": "plugins/unicode", "to": "core"}]}
```

- `from` and `to` are paths relative to the root: a file or a folder. Each path belongs to the unit that contains it. A use inside one unit is ignored. A use of a path outside the project is ignored.
- `covers` lists folders, relative to the root, for which the list is complete: every use from a file below such a folder is in `uses`. A unit is covered when its folder or a folder above it is listed.
- `source` says what produced the file. It is printed and not interpreted.
- The format is defined in a new reference chapter, `docs/references/observed.md`, with a JSON Schema at `https://unifold.md/0.3/observed.schema.json`. The chapter gives, as examples and not as part of the standard, one command each for `cargo metadata`, `go list` and dependency-cruiser that writes the file.

### Reading it

- `check --observed FILE` reads one file. The option can be given more than once.
- The root key `observed` lists files, relative to the root, that `check` reads when they exist. A listed file that does not exist gives an `info` finding, because CI may write it only in some jobs.
- A file that does not parse, or that has an unknown version, is an error of the run (exit code 2), not a finding.

### Findings

| Rule | Severity | What must hold |
|---|---|---|
| `O1` | warn | A use from a covered unit A to a unit B is allowed by the map: a need of A, followed to its final provider, reaches B or a unit below B. A use from A to code of an ancestor that lies in no child is reported too, as wiring.md already says that this direction is not modelled. |
| `O2` | warn | A connection of kind `library` whose user and final provider are both covered has at least one observed use from the user to the provider. Calls over a network are not seen by import scanners, so other kinds are not compared. |
| `O3` | info | The coverage: "observed: 9 of 22 units, from cargo metadata". |

- The fix of `O1` names the need to declare and the `unifold wire` command where [0060](0060-add-a-command-that-writes-a-connection-through-every-level.md) is accepted. The fix of `O2` says to remove the connection, or to correct the observation.
- The severity is `warn` because conformance stays a property of the committed files. An observation depends on a build, a machine and a commit. A project that wants the comparison to fail its build runs `check --strict`.
- The ids `D1` to `D3` are not reused. The letter `O` is new.

### Where it is written

- [spec.md](../references/spec.md) section 5 gets two lines: if a project supplies observed dependencies, a conforming checker reports uses that the map does not allow, and the units the observation covers.
- [rules.md](../references/rules.md) gets the three rules, the tool gets them, and `tests/conformance.py` gets a case for each.
- The skill `unifold-convert` writes the observation file during a conversion, when the build tool can produce one, and keeps it as the input of later checks.
- No extractor is added to this repository. The file lists uses, never units, so the units of a repository stay a judgement of a person or an agent ([0034](0034-convert-a-repository-with-a-skill-instead-of-drafting-manifests.md)).

This amends 0047: "the checker reads never code" and the removal of `D1` to `D3`, `deps` and `--deps` stand. Its "keeping the code and the map in step is part of each change and of its review" becomes: part of review, and part of the check for the units that an observation covers.

### Consequences

- Good: a project that supplies the file gets back what 0047 removed, for exactly the units the file covers, and the output says which units those are.
- Good: the tool learns no language. An extractor improves without a release of the tool.
- Good: code of a parent that uses a child without a need is found, which [0048](0048-write-every-connection-out-and-let-a-unit-wire-its-own-need.md) could only ask for.
- Bad: a project has to write or find the command that produces the file. Until it does, nothing changes.
- Bad: a wrong `covers` gives false confidence. The output says "observed", and an observation is only as complete as its source.
- Bad: calls over a network, plug-ins loaded at run time and generated code are not seen unless the source lists them.
- Bad: one more format to version and keep stable.
