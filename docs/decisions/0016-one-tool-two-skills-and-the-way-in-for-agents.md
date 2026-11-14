---
status: accepted
date: 2026-11-03
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# One tool, two skills, and the way in for agents

## Context and Problem Statement

The standard promises "checked" and "generated", which needs a tool, and it is meant to be used with coding agents, which need to find the map and the procedures from where they start. How is the tool delivered, and how does an agent find its way in?

## Decision

- The reference tool is one Python file, published on PyPI as `unifold`, with the commands `init`, `check`, `show`, `capability`, `impact`, `brief`, `trace`, `tree`, `model`, `explore` and `rules`, each with `--json`. Diagrams are drawn by `explore` only. Its conformance tests are data that another implementation can run.
- Two skills in the Agent Skills format travel with the tool: `unifold`, the procedures for reading and changing a project, with templates for every file and one procedure per task; and `unifold-convert`, the procedure that brings an existing repository into the map. No script derives units from code: a person or an agent chooses them.
- `unifold init --agents` installs the skills into `docs/skills/` of the root, writes their stubs into `.agents/skills/` and `.claude/skills/`, and adds the unifold block to the root `AGENTS.md`. Skills of a project live in `docs/skills/` of their unit; `check --fix` keeps the stubs current.
- An agent reads the root `AGENTS.md` and the `README.md` of its unit, runs `unifold show` in the folder of its task, and opens further files only as the task needs. It runs `check` when it stops, not after every edit.

## Consequences

- Good: every agent with a shell has the same way in, and a project ships nothing of the standard but the skills it chose to install.
- Bad: an agent that searches other folders for skills finds the stubs only through `AGENTS.md`.
