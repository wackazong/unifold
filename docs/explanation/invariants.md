# Invariants of unifold

What is true of the standard, the skills and the tool at every moment. A
change that breaks one of these lines is a change to the standard and needs
a decision.

- Everything normative for level `core` is in
  [spec.md](../references/unifold/spec.md), which has at most 200 lines and
  defines nothing by reference to another chapter. The other chapters
  explain and add no rule for `core`.
- At level `core` no finding depends on the content of a prose file.
- The standard depends on no programming language, build system or code
  host. The extractors are features of the reference tool.
- The chapters in `docs/references/unifold/` are published at
  `https://unifold.md`. They link only to each other, to the explanation
  and tutorial files of this repository that are published beside them,
  and to full URLs. The skills are installed into other projects and link
  to the site only by `https://unifold.md/...` URL. Both can be used
  outside this repository.
- A finding of the tool exists in three places that agree:
  [rules.md](../references/unifold/rules.md), the tool, and a case in
  `tests/conformance.py`. Prose chapters do not cite rule ids.
- Every change to the standard is recorded as a decision with
  `status: proposed`. Only a person sets `accepted`.
- A claim about a tool, a study or a product carries a link to its source.
- The schema of the manifest is served at
  `https://unifold.md/0.1/unifold.schema.json`.
- Nothing of the standard is copied into a project
  ([0028](../decisions/0028-reference-the-standard-instead-of-copying-it.md)).
  A project names the version it follows in its root manifest.
- Structure is declared once and generated; reasons are written. No
  hand-written file lists units, capabilities or connections.
- The standard obeys itself, as far as a rule can apply to a single unit.
  This repository is at level `full`, and its documents are sorted the way
  it asks of every project.
