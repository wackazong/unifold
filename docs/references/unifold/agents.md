# Coding agents

How a coding agent finds out that a repository uses unifold, what it reads, and what it should not trust.

## Three ways in

| Way | What it is | When the agent sees it |
|---|---|---|
| `AGENTS.md` | A generated file per unit: a pointer to `README.md`, the documents of the unit by kind, its skills. The root file also carries the unifold block: what unifold is, the commands `show`, `capability` and `check`, and an index of the units (name, path, summary) for projects up to 40 units | Always, where the agent loads `AGENTS.md` |
| The skills | `unifold-convert`, the procedure that brings a repository into the format, and `unifold`, the procedures for reading and changing a unifold project | When the agent decides that the task calls for it |
| The tool | `unifold show`, `capability`, `impact` and `check`, each with `--json`; optionally as an MCP server | When the agent runs it |

`unifold init --agents` sets up all three: it installs the skills in `docs/skills/` of the root, writes the stubs described below, and adds the block to the root `AGENTS.md` ([tool.md](tool.md)). Why there are three ways and not one is in [reasoning.md](../../explanation/reasoning.md).

## Where skills are found

No agent searches `docs/skills/`. unifold keeps skills there, next to the code they concern, and `unifold skills sync` writes a generated stub for each into `.agents/skills/` and `.claude/skills/` at the root. The stub of a skill of the root unit keeps the name of the skill, for example `unifold`. The stub of a skill of another unit is named `<unit>-<skill>`; if two units would get the same name, the path of the unit with `-` for `/` takes the place of its name. A stub has the description of the skill, and its body says which file to read. Stubs are files, not symbolic links, so that they work on every operating system and relative links in the skill stay valid. Commit them. The checker reports stale stubs when the folders exist.

`.agents/skills` is the folder that the Agent Skills project recommends to all clients
([source](https://agentskills.io/client-implementation/adding-skills-support.md)).

## What each agent reads

| Agent | `AGENTS.md` | Folder in which it finds the stubs |
|---|---|---|
| Claude Code | Read natively since v2.1.277, but only if no `CLAUDE.md` or `CLAUDE.local.md` exists at or above the working directory; otherwise `CLAUDE.md` has to import it with `@AGENTS.md` ([memory](https://code.claude.com/docs/en/memory)) | `.claude/skills` ([skills](https://code.claude.com/docs/en/skills)) |
| Codex CLI | From the root down to the working directory, at start, up to 32 KiB together ([docs](https://learn.chatgpt.com/docs/agent-configuration/agents-md)) | `.agents/skills`; the list of skills is cut at 2 % of the context or 8,000 characters ([docs](https://learn.chatgpt.com/docs/build-skills)) |
| Cursor | Root and nested files, combined with the parents ([rules](https://cursor.com/docs/context/rules)) | `.agents/skills`, `.claude/skills` ([skills](https://cursor.com/docs/skills)) |
| GitHub Copilot | Anywhere in the repository; the nearest file takes precedence ([docs](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)) | `.agents/skills`, `.claude/skills` ([docs](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)) |
| Gemini CLI | Only when the setting `context.fileName` names it; the default is `GEMINI.md` ([docs](https://geminicli.com/docs/cli/gemini-md/)) | `.agents/skills` ([docs](https://geminicli.com/docs/cli/skills/)) |
| Windsurf | The root file always; nested files for their folder ([docs](https://docs.devin.ai/desktop/cascade/agents-md)) | `.agents/skills` ([docs](https://docs.devin.ai/desktop/cascade/skills)) |
| opencode | Not verified | `.agents/skills`, `.claude/skills` ([docs](https://opencode.ai/docs/skills)) |
| Amp | Not verified | `.agents/skills`, `.claude/skills` ([docs](https://ampcode.com/manual/agent-skills.md)) |
| Kiro | Not mentioned in its documentation of skills | Not reached: it reads `.kiro/skills` only ([docs](https://kiro.dev/docs/skills/)) |
| Aider | Nothing is loaded automatically | No skills |

Consequences:

- `unifold init --agents` prints a hint when a `CLAUDE.md` exists that does not mention `AGENTS.md`.
- Copilot may use only the nearest `AGENTS.md`. Every unit's `AGENTS.md` therefore carries the one line "unifold unit; run `unifold show` here."
- Codex stops loading at 32 KiB. The generated `AGENTS.md` is therefore short: pointers, not text ([documents.md](documents.md)).
- Every agent in the table can run a shell command. The tool is the one way in that works for all of them.

## What the agent reads, in order

1. The `AGENTS.md` files that its harness loads, and the `README.md` each of them points to. Its `## Why` is what cannot be derived from code.
2. `unifold show` in the folder of the task. It prints the unit, its capabilities and needs, who finally provides and uses them, the status of every unit it mentions, and the skills and decisions of the unit.
3. Only then further files: `docs/explanation/context.md`, a contract, the explanation file the task needs. The `unifold` skill has the table of what to read for which task.

`unifold impact` answers "what is affected if I change this": the units that depend on a unit or capability, through the whole tree, and the context items that cite its files.

## What an agent must not take as fact

| Sign | Meaning |
|---|---|
| `status: planned` | The text describes an intention. The code may not exist. |
| A decision with `status: proposed` | Nobody has agreed to it yet. Only accepted decisions bind. |
| A warning about a stamp | A restatement in `docs/explanation/context.md` may no longer match its source. Read the source. |
| `summary: TODO` | A placeholder that nobody has completed. |
| `verified-by` | A pointer to tests. unifold does not run them. |

`show` and `capability` print the status of every unit they mention and mark planned units and proposed decisions.

## Hooks, continuous integration, MCP

- Run `unifold check` at the end of an agent's turn, not after every edit: a unit that is being added is broken for a moment. `check --fix` writes the generated files and no stamp: a stamp is written only by `unifold stamp`, after `Says` was compared with its source. `check --json` gives findings with file, line and a proposed fix.
- `unifold mcp` is an optional MCP server over standard input and output with the tools `show`, `capability`, `impact`, `check` and `tree`, for agents that should read the map without shell access.

The commands, the JSON shapes, a pre-commit hook and a CI job are in
[tool.md](tool.md).
