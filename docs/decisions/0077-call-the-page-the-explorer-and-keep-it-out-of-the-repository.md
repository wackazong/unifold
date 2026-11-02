---
status: accepted
date: 2026-11-02
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Call the page the explorer, open it with `unifold explore`, and keep it out of the repository

## Context and Problem Statement

[0005](0005-generate-diagrams-as-mermaid-with-link-tables.md) added an HTML page in which every box of the map is clickable. The command was `unifold site`, the file `unifold.html` in the root of the project, and the examples committed theirs: 1.4 MB for plantwatch, rewritten with every change to the tool or the map and checked by nothing. Neither the README nor the site said what the page is. The page had three names: site, explorer, `unifold.html`.

## Considered Options

- Keep `unifold site` and `unifold.html` in the root
- A generated file of the standard, `docs/diagrams/explorer.html`, written by `generate`, checked and committed like the diagrams
- A view: `unifold explore` writes the page outside the repository and opens it in a browser; `-o` puts it where a project publishes it

## Decision Outcome

Chosen option: "a view", because the page is read in a browser, not in a clone, a review or on a code host, where the Markdown diagrams of 0005 already serve, so nothing is gained by committing it, and a file of 1 MB that changes with every edit of the map is a cost that [0053](0053-commit-the-generated-files.md) weighed for diagrams a hundred times smaller.

- The page is called the explorer everywhere: in the tool, in the documents and on the site.
- `unifold explore [PATH]` writes `explorer.html` under the temporary folder of the system, one per project name, and opens it in the browser of the system. `--no-open` only writes; `-o FILE|DIR` writes elsewhere, for a build.
- The examples commit no page. `site/build.py` runs `unifold explore` for every example and publishes the result at `/examples/<name>/`.
- The standard does not change: the explorer is not a generated file of section 7.

### Consequences

- Good: one name, one command, nothing to commit, never stale.
- Good: the examples lose 1.6 MB of generated HTML.
- Bad: a clone does not contain the page; whoever wants it runs one command.
- Bad: `unifold site` no longer exists; the tool version changes with the next release.
