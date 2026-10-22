# Invariants of unifold

What is true of the standard, the skills and the tool at every moment. A change that breaks one of these lines is a change to the standard and needs a decision.

- Everything normative about manifests, wiring, generated files and the comparison with code is in [spec.md](../references/spec.md), which has at most 200 lines. The document conventions are in [documents.md](../references/documents.md) and [writing.md](../references/writing.md); the other chapters explain and add no rule.
- No finding depends on the meaning of a prose file: the checker reads links, headings, front matter and length.
- The standard depends on no programming language, build system or code host. The extractors are features of the reference tool.
- The reference chapters, the explanation files and the tutorial are published at `https://unifold.md`; a relative link to any other file of this repository becomes a link to the repository there. The skills are installed into other projects, so they link outside themselves only by `https://unifold.md/...` URL.
- A finding of the tool exists in three places that agree: [rules.md](../references/rules.md), the tool, and a case in `tests/conformance.py`. Prose chapters do not cite rule ids.
- Every change to the standard is recorded as a decision with `status: proposed`. Only a person sets `accepted`.
- A claim about a tool, a study or a product carries a link to its source.
- The schema of the manifest is served at `https://unifold.md/0.1/unifold.schema.json`.
- Nothing of the standard is copied into a project ([0028](../decisions/0028-reference-the-standard-instead-of-copying-it.md)). A project names the version it follows in its root manifest.
- Structure is declared once and generated; reasons are written. No hand-written file lists units, capabilities or connections.
- The standard is tried on its examples. This repository is a specification, and a specification is not a unit: it has no manifest, and its documents follow the document conventions by choice, not by check.
