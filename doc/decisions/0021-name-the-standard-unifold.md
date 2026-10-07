---
status: proposed
date: 2026-10-07
---
# Name the standard unifold

## Context and Problem Statement

The working name was "youmedoc", to be read as "you, me, doc". A reviewer in
the role of an open-source user read it as "youmed-oc". The name said who the
documents are for. It did not say what the standard is made of: units in
folders, nested to any depth, of which a reader opens only what the task
needs.

The name is also an identifier. It is the root key of the manifest, the name
of the folder that projects copy, the name of the tool and the marker in
generated files.

## Considered Options

- Keep "youmedoc"
- "unifold": unit, unity, folder, unfold
- "unitect": unit, unite, architect
- "holon": Koestler's word for something that is a whole and a part
- "unitdown": units all the way down, in the Markdown family
- "recunit": recursive unit

## Decision Outcome

Chosen option: "unifold", because it is the only candidate that carries the
unit, the recursion and the economy of reading in one word, and it works as a
command and as a manifest key. "holon" needs an explanation and adds a second
word next to "unit". "unitect" says nothing about nesting. "unitdown" reads
as "a unit is down". "recunit" reads as a test framework.

The name is written in lower case everywhere, as the identifiers are.

### Consequences

- Good: the name says what a reader does with the tree: unfold one unit.
- Good: the package name was free on PyPI, npm and crates.io on the date of
  this decision.
- Bad: the name is not unused. A protein-structure model is called Uni-Fold,
  a payments company uses `unifold.io`, and a software studio uses
  `unifold.dev`. The addresses with `.com`, `.org`, `.net` and `.app` are
  registered by others.
- Bad: the name no longer says "for people and agents". The first lines of
  the root `README.md` say it instead.
- Bad: search engines suggest "unfold".
- Neutral: the term "unit" and the file name `unit.yaml` stay as they are.
- Neutral: the standard is published at `https://unifold.md`. The ending is
  the one of Markdown files, which is what the standard consists of.
