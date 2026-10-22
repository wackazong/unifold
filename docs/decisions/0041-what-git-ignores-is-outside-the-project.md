---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# What git ignores is outside the project

## Context and Problem Statement

The checker walked every folder under the root except dot folders, a few well-known build outputs and the folders named by `ignore` in the root manifest. Build output, caches, virtual environments and generated files that a repository already excludes in `.gitignore` had to be named a second time, and a stray `unifold.yaml` or Markdown file in such a folder became a unit or a checked document.

## Considered Options

- Keep the manifest's `ignore` list as the only exclusion
- Read `.gitignore` files in the tool itself
- Ask git which untracked paths it ignores, and treat them as absent

## Decision Outcome

Chosen option: "ask git", because git already knows the answer, including `.git/info/exclude` and the global excludes, and a second implementation of the pattern language would drift from it.

- A path that `git ls-files --others --ignored --exclude-standard` lists is not searched for units, documents or dependencies. A committed file is part of the project even if a pattern matches it.
- Without git, or outside a work tree, nothing changes.
- `ignore` in the root manifest stays, for committed third-party code.

### Consequences

- Good: the usual exclusions of a repository need no repetition.
- Bad: the result of `check` depends on git being installed and on the gitignore files, which the manifests do not show.
