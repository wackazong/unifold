# JSON output of the reference tool

Every command of the [tool](tool.md) accepts `--json` and then prints one JSON value on standard output. Paths are relative to the project root, with forward slashes; the root itself is `"."`. Later versions may add keys. The output of `model` has a schema of its own, versioned with the standard, and a key of it is never removed within a version.

## Failure

When a command cannot run, it prints this object, a message on standard error, and exits with 2 (3 for an internal error):

```json
{"ok": false, "error": {"code": "no-project", "message": "no unifold project found: ..."}}
```

| `code` | Meaning |
|---|---|
| `usage` | Wrong command line |
| `no-project` | No `unifold.yaml` with the key `unifold` here or above |
| `bad-root` | The root manifest does not parse or states another version than 0.3; `check` reports it as a finding instead |
| `no-such-path`, `not-a-folder`, `not-a-root` | The path given does not fit the command |
| `unknown-capability`, `unknown-rule`, `nested-project` | The thing asked for does not exist here |
| `not-writable`, `io`, `no-mermaid` | A file could not be read or written |
| `internal` | A bug in the tool |

For `check`, the object also has `summary` and an empty `findings` list, so that a reader of findings needs no second code path.

## check

```json
{"ok": false,
 "summary": {"units": 12, "error": 1, "warn": 0, "info": 0, "rules": {"W2": 1},
             "ignored": {"C2": 3}, "root": "/work/shop", "tool": "0.3.1"},
 "findings": [
  {"rule": "W2", "severity": "error", "file": "cloud/unifold.yaml", "line": 14,
   "message": "need 'alerts.push' has no provider",
   "fix": "Add `alerts.push: <provider>` to the wiring of this manifest, or declare a need `push` here to pass it up.",
   "url": "https://unifold.md/rules#w2"}]}
```

- `ok` is true when the exit code is 0: no error, and with `--strict` no warning.
- `severity` is `error`, `warn` or `info`. `line` is a number or `null`. `file` is the file to change; for a missing `README.md` or `SKILL.md` it is the folder.
- `fix` says what to do, specific to the finding where the tool can tell.
- `ignored` counts the findings that `--ignore` dropped, per rule; they are not in `findings` and not in the counts.
- With `--fix`, `summary.fixed` has `written`, `removed` and `refused` (lists of paths). `--fix` writes generated files only, never a stamp.
- `--format github` prints the same findings as lines `::error file=cloud/unifold.yaml,line=14,title=unifold W2::message Fix: ...`, with paths relative to the current folder, then the summary line.

## show

```json
{"name": "serial", "path": "transport/serial",
 "responsibility": "Moves frames through the serial port with deadlines",
 "kind": "adapter", "status": "planned", "owner": null,
 "secret": {"what": "opening the port, writing to it and reading it with deadlines",
            "decision": "transport/docs/decisions/0001-the-line-is-one-unit.md"},
 "not": [{"text": "frame layout", "need": "frames"}, {"text": "retries", "need": null}],
 "manifest": "transport/serial/unifold.yaml",
 "parent": {"path": "transport", "name": "transport", "status": "planned", "responsibility": "..."},
 "children": [], "nested-projects": [],
 "capabilities": {"transport": {
   "kind": null, "summary": "...", "contract": "docs/references/transport.md", "parts": null,
   "used-by": [{"unit": "session", "status": "planned", "need": "transport", "config": null}]}},
 "needs": {"frames": {
   "kind": null, "summary": "...", "contract": "docs/references/frames.md", "parts": ["encode"],
   "optional": false, "platform": false,
   "provided-by": [{"unit": "codec", "status": "planned", "capability": "frames", "config": null}]}},
 "scenarios": [{"unit": ".", "name": "open", "summary": "The host opens a session"}],
 "skills": [{"name": "add-a-quantity", "path": "...", "description": "..."}],
 "decisions": [{"path": "...", "title": "...", "status": "proposed"}],
 "documents": {"tutorials": [], "references": ["..."], "explanation": ["..."]},
 "diagrams": ["transport/serial/docs/diagrams/context.md"],
 "files": ["transport/serial/README.md", "..."]}
```

- `used-by` and `provided-by` are resolved through the whole tree: they name the units whose own code is on the other side. A unit above can be such a user, when it wires a need of its own to this capability; a need that a unit meets inside is provided by a unit below it, never from outside.
- The other form of an entry: `{"outside": true, "root-capability": "api"}` and `{"outside": true, "root-need": "clock", ...}` for the world outside the project.
- `config` is the name of the alternative, or `null`. `parts` is the list under `contract`, or `null` for the whole contract.
- `contract` is a path relative to the root. Both sides of a connection name the same contract, so an entry under `used-by` or `provided-by` repeats none.
- `scenarios` lists the scenarios whose hops name the unit or use a wiring line of it, with the unit that holds each.
- A `status` other than `active`, and a decision status other than `accepted` or `derived`, means: not in force. The text output marks these in brackets.

## capability

```json
{"unit": "db", "name": "store", "side": "capabilities",
 "ends": [
  {"unit": "db", "status": "planned", "side": "capabilities", "name": "store", "kind": null,
   "summary": "Keeps things", "contract": "docs/references/store.md", "parts": null,
   "optional": null, "readme": "text of the README section, or null"},
  {"unit": "web/inner", "status": "active", "side": "needs", "name": "store", "...": "...",
   "optional": false, "config": null}]}
```

The first end is the capability or need asked for; the others are every final user or provider. An end outside the project has `"outside": true`.

## impact

```json
{"unit": "db", "status": "planned", "capability": null, "file": null,
 "dependents": [{"unit": "web/inner", "status": "active", "distance": 1,
                 "via": "need 'store' is met by capability 'store' of db"}],
 "exposed-as": [{"unit": ".", "capability": "store"}],
 "outside": ["store"], "root-capabilities-affected": ["api", "store"],
 "citations": [{"file": "web/docs/explanation/context.md", "line": 12, "cites": "db/README.md",
                "kind": "context-item", "title": "db: storage rules",
                "says": "...", "stamp": "current"}]}
```

`distance` 1 is a direct user, which can be the parent when its own need is wired to the unit; higher numbers depend on a dependent. `exposed-as` lists the units above that provide the capability as their own; `outside` the capabilities of the root through which the world uses it directly; `root-capabilities-affected` every capability of the root that depends on it. `stamp` is `current`, `stale` or `missing`.

## tree, cited-by, skills, rules

`tree` prints a list, the root first:

```json
[{"path": "cloud", "name": "cloud", "depth": 1, "status": "planned", "kind": "system",
  "responsibility": "...", "parent": ".", "capabilities": ["public-api"],
  "needs": ["push-service"], "children": ["cloud/platform"], "nested-projects": []}]
```

`cited-by` prints the `citations` rows of `impact`; a row of kind `link` has no `title`, `says` or `stamp`. `skills` prints `[{"name", "unit", "path", "description"}]`. `rules` prints `[{"id", "severity", "what", "fix", "url"}]`.

## model

`unifold model` prints the resolved map of the whole project. Its schema is `unifold-model` 0.3 and changes only with a decision; within 0.3 keys are added, never removed or changed in meaning. Keys that start with `x-` in a manifest, a capability, a need or a scenario are passed through untouched under `x`. A process tool reads this and nothing else.

```json
{"unifold-model": "0.3", "tool": "0.3.1", "project": "serial-line", "root": "/work/serial-line",
 "units": [
  {"path": "transport", "name": "transport", "parent": ".", "children": ["transport/framing", "transport/serial"],
   "responsibility": "Sends and receives frames over the serial line", "kind": "adapter",
   "status": "planned", "owner": null, "readme": "transport/README.md",
   "secret": {"what": "how frames travel over the line", "decision": "transport/docs/decisions/0001-the-line-is-one-unit.md"},
   "not": [{"text": "frame layout", "need": "frames"}, {"text": "retries after a failed write", "need": null}],
   "capabilities": [
    {"name": "transport", "summary": "...", "kind": null, "contract": "docs/references/transport.md", "parts": null,
     "contract-parts": [{"name": "send", "kind": "command"}, {"name": "receive", "kind": "query"}], "fake": "described",
     "final-users": [{"unit": "session", "need": "transport", "config": null}], "x": {}}],
   "needs": [
    {"name": "uart", "summary": "...", "kind": null, "contract": "docs/references/uart.md", "parts": null,
     "contract-parts": [{"name": "write", "kind": "command"}], "fake": "described", "optional": false, "platform": false,
     "final-providers": [{"outside": true, "root-need": "uart", "config": null}], "x": {}}],
   "wiring": [
    {"key": "transport", "value": "serial.transport", "alternative": null, "form": "implemented-by",
     "user": null, "need": null, "provider": "transport/serial", "capability": "transport", "to-need": null},
    {"key": "serial.uart", "value": "uart", "alternative": null, "form": "passed-up",
     "user": "transport/serial", "need": "uart", "provider": null, "capability": null, "to-need": "uart"}],
   "scenarios": [
    {"name": "reassemble", "summary": "Two frames arrive in one read", "source": "proto §4.3",
     "expect": "receive returns the first payload", "hops": [
      {"caller": "transport", "target": "serial", "part": "receive", "caller-unit": null, "target-unit": "transport/serial",
       "contract": "docs/references/transport.md", "via": [{"unit": "transport", "key": "transport"}]}],
     "x": {}}],
   "decisions": [{"path": "transport/docs/decisions/0001-the-line-is-one-unit.md", "title": "The line is one unit",
                  "status": "proposed", "date": "2026-10-27", "derived-from": null, "answer": null}],
   "documents": {"tutorials": [], "references": ["transport/docs/references/framing.md"], "explanation": []},
   "x": {}}],
 "root-needs": [{"name": "uart", "platform": false, "reached-by": ["transport/serial"]},
                {"name": "clock", "platform": true, "reached-by": ["session"]}]}
```

- `units` holds every unit, the root first, then by path. `parent` is `null` for the root.
- `form` of a wiring row is `connection` (a need of a child met by a sibling), `passed-up` (to `to-need` of this unit), `met-inside` (a need of this unit, `user` is this unit) or `implemented-by` (`capability` is the own capability named by `key`). One row per alternative; `alternative` is its name or `null`.
- `final-users` and `final-providers` are the `used-by` and `provided-by` of `show`, without status. `contract-parts` lists the parts the contract defines, with their kind, or is `null` when the entry names no contract. `fake` is `real` when the contract's `## Fake` section says `the real implementation`, `described` when it says anything else, and `null` without the section or the contract.
- A hop's `caller` and `target` are the names as written; `caller-unit` and `target-unit` are the paths of the units they name, or `null` for a capability or need of the holding unit. `via` lists the wiring lines the hop uses, from the top down, as the unit that holds the line and the key of the line; it is empty for a hop between a capability and a need of a unit without children. `contract` is the document in which `part` was looked up. An unresolved hop has `unresolved`, the hop as written, and `error`.
- `answer` of a decision is `null` when it has no `## Answer` section, else `{"empty": true}` or `{"empty": false}`: an open question of a process is a decision whose `## Answer` is empty.
- `reached-by` names the units whose own code finally uses a need of the root.

## Commands that write

`init`: `{"ok": true, "root", "written": [paths], "notes": [text], "units": 1}`; `written` holds the root manifest, if `init` wrote it, and the generated files. `generate` and `skills sync`: `{"ok", "written", "removed", "refused"}`. `site`: `{"ok": true, "written": "/abs/unifold.html"}`. `stamp` names every stamp it wrote; `action` is `added` or `refreshed`:

```json
{"ok": true, "stamped": 1, "items": [
  {"file": "web/docs/explanation/context.md", "line": 12, "cites": "db/README.md",
   "title": "db: storage rules", "action": "refreshed"}]}
```
