# Invariants of unifold

What is true of the standard, the skills and the tool at every moment. A change that breaks one of these lines is a change to the standard and needs a decision.

- Every rule is in a chapter that [spec.md](../references/spec.md) names as the standard; the other chapters explain and add no rule.
- No finding depends on the meaning of a prose file. What the checker reads is listed once, in [spec-conformance.md](../references/spec-conformance.md#5-documents); it judges no sentence.
- The standard and the tool depend on no programming language, build system or code host: nothing reads code.
- The reference chapters, the explanation files and the tutorial are published at `https://unifold.md`; a relative link to any other file of this repository becomes a link to the repository there. The skills are installed into other projects, so they link outside themselves only by `https://unifold.md/...` URL.
- A finding of `check` exists in the rule table of the tool and in a case in `tests/conformance.py`. [rules.md](../references/rules.md) is generated from the table by the site build, which reports it when it is stale. Prose chapters do not cite rule ids.
- Every change to the standard is recorded as a decision with `status: proposed`. Only a person sets `accepted`.
- A claim about a tool, a study or a product carries a link to its source.
- The schema of the manifest is served at `https://unifold.md/<version>/unifold.schema.json`, and a version that was published stays there.
- Nothing of the standard is copied into a project ([0018](../decisions/0018-name-version-licence-and-what-ends-up-in-a-project.md)). A project names the version it follows in its root manifest.
- Structure is declared once and generated; reasons are written. No hand-written file lists units, capabilities or connections, with one exception: the hops of a scenario in a manifest, which are checked declarations like wiring lines.
- The tool reads one version of the standard, the current one. A manifest never changes its meaning while its version string stays the same.
- The standard is tried on its examples. This repository is a specification, and a specification is not a unit: it has no manifest, and its documents follow the document conventions by choice, not by check.
