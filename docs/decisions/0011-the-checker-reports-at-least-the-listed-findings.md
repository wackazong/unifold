---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# The checker reports at least the listed findings

## Context and Problem Statement

A standard that only one tool can interpret is a description of that tool. A second implementation must report the same findings, with the same severity, for the same project, and a project must know what makes it conformant. What does a checker guarantee?

## Decision

- A conforming checker reads a project, changes nothing, and reports findings with a severity: `error` for what makes the map inconsistent, `warn` for what makes it better but is not needed for consistency, `info` for a fact worth knowing. The rules page, which is generated from the rule table of the reference tool, lists every finding with its severity, each with a rule id, a fix text and a test case; a conforming checker reports at least these, with the same severity.
- The checker reads links, headings, front matter and length; of a contract the `Carried by:` line, the field lines of each part, the names in code font under `Errors:`, the signature block, the examples table and the `## Qualities` table; of a decision its file name and front matter. It does not follow the `## States` table. Inside a fenced block it reads only the names of the contract's types, to tell whether a part uses a type, and it judges no sentence: a word in a sentence is no use of a type.
- A project conforms to unifold 0.4 when a conforming checker reports no error. No error means consistent, not correct: no checker reads the code.
- The rule table of the reference tool is the source of the rules page; a meta test keeps the standard, the tool and the test cases in step.

## Consequences

- Good: a second tool can be written from the text, and a project knows what conformance means.
- Bad: every new rule costs a rule text, a fix text and a test case.
