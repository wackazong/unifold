---
status: rejected
date: 2026-10-24
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Promise consistency, and agreement with the code only where it is observed

## Context and Problem Statement

The front page promises: "Keep your documentation, architecture, and project structure aligned." The same line is on the site, written by `site/build.py`. Since [0047](0047-remove-the-comparison-with-code.md), the check proves less: the manifests, the generated files and the links agree with each other. The code is not read.

The other chapters already say this. Goal 4 of the [requirements](../explanation/requirements.md) says that a clean check means that the files agree, and that whether the code follows them is for tests and review. The [risks](../explanation/risks.md) say that a clean check is not a true map. Only the front page, which every reader sees first, promises more. A reader who finds the first drift that the check did not report stops trusting the rest.

## Considered Options

- Keep the line
- Keep the line and qualify it in the questions of the README
- Narrow the line to what the check holds, and widen it again only as far as [0050](0050-compare-the-wiring-with-observed-dependencies-that-the-project-supplies.md) allows

## Decision Outcome

Chosen option: "narrow the line", because the first sentence a reader sees has to be true without the questions below it.

- The title stays "unifold: architecture as code": the architecture is declared in files of the repository and checked, as infrastructure is in infrastructure as code.
- The quote under the title becomes: "Your folders are your architecture. Each folder says what it provides and needs, the folder above connects them, and a check keeps the map, the diagrams and the documents consistent."
- "How it works" gets one sentence after the error example: "The check compares files with files. Whether the code follows the map is for review, and, where the project supplies observed dependencies, for the check." The second half is written only when 0050 is accepted.
- The site, the description of the package on PyPI and the description of the GitHub Action use the same words.
- [invariants.md](../explanation/invariants.md) gets a line: the front page, the site and the package descriptions promise no more than section 5 of [spec.md](../references/spec.md) guarantees.

### Consequences

- Good: the first sentence is true, and it says the same as the requirements and the risks.
- Good: the invariant makes the next overpromise a change that needs a decision.
- Bad: the pitch is weaker. "Aligned with the code" is what most readers want, and the line now says that unifold does not give it by default.
- Bad: the wording depends on 0050. If 0050 is rejected, the second sentence stays "Whether the code follows the map is for review."
