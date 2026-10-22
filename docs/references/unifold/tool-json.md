# JSON output of the reference tool

Every command of the [tool](tool.md) except `mcp` accepts `--json` and then prints one JSON value on standard output. Paths are relative to the project root, with forward slashes; the root itself is `"."`. Later versions may add keys.

## Failure

When a command cannot run, it prints this object, a message on standard error, and exits with 2 (3 for an internal error):

```json
{"ok": false, "error": {"code": "no-project", "message": "no unifold project found: ..."}}
```

| `code` | Meaning |
|---|---|
| `usage` | Wrong command line |
| `no-project` | No `unifold.yaml` with the key `unifold` here or above |
| `bad-root` | The root manifest does not parse or states an unsupported version; `check` reports it as a finding instead |
| `no-such-path`, `not-a-folder`, `not-a-root` | The path given does not fit the command |
| `unknown-capability`, `unknown-rule`, `nested-project` | The thing asked for does not exist here |
| `bad-argument` | MCP only: an argument of a tool has the wrong type or is missing |
| `not-writable`, `io`, `no-mermaid` | A file could not be read or written |
| `internal` | A bug in the tool |

For `check`, the object also has `summary` and an empty `findings` list, so that a reader of findings needs no second code path.

## check

```json
{"ok": false,
 "summary": {"units": 12, "error": 1, "warn": 0, "info": 0, "rules": {"W2": 1},
             "root": "/work/shop", "tool": "0.1",
             "dependencies": {"observed": 19, "extracted": true, "notes": []}},
 "findings": [
  {"rule": "W2", "severity": "error", "file": "cloud/unifold.yaml", "line": 14,
   "message": "need 'alerts.push' has no provider",
   "fix": "Add `alerts.push: <provider>` to the wiring of this manifest, or declare a need `push` here to pass it up.",
   "url": "https://unifold.md/rules#w2"}]}
```

- `ok` is true when the exit code is 0: no error, and with `--strict` no warning.
- `severity` is `error`, `warn` or `info`. `line` is a number or `null`. `file` is the file to change; for a missing file of a unit it is the folder of the unit.
- `fix` says what to do, specific to the finding where the tool can tell.
- With `--fix`, `summary.fixed` has `written`, `removed` and `refused` (lists of paths). `--fix` writes generated files only, never a stamp.
- `--format github` prints the same findings as lines `::error file=cloud/unifold.yaml,line=14,title=unifold W2::message`, with paths relative to the current folder.

## show

```json
{"name": "rules", "path": "cloud/services/alerts/rules",
 "summary": "Evaluates readings against the thresholds of a plant",
 "kind": "library", "status": "planned", "owner": "backend team",
 "manifest": "cloud/services/alerts/rules/unifold.yaml",
 "parent": {"path": "cloud/services/alerts", "name": "alerts", "status": "planned", "summary": "..."},
 "children": [], "nested-projects": [],
 "capabilities": {"evaluation": {
   "kind": "library", "summary": "...", "contract": "cloud/services/alerts/rules/docs/references/evaluation.md",
   "verified-by": null,
   "used-by": [{"unit": "cloud/services/alerts/server", "status": "planned",
                "need": "evaluation", "config": null}]}},
 "needs": {"thresholds": {
   "kind": "library", "summary": "...", "contract": "...", "verified-by": null, "optional": false,
   "provided-by": [{"unit": "cloud/services/alerts/plant-lookup", "status": "planned",
                    "capability": "thresholds", "verified-by": null,
                    "config": null, "via": []}]}},
 "skills": [{"name": "add-a-quantity", "path": "...", "description": "..."}],
 "decisions": [{"path": "...", "title": "...", "status": "proposed"}],
 "diagrams": ["cloud/services/alerts/rules/docs/diagrams/context.md"],
 "files": ["cloud/services/alerts/rules/README.md", "..."]}
```

- `used-by` and `provided-by` are resolved through the whole tree: they name the units whose own code is on the other side.
- The other form of an entry: `{"outside": true, "root-capability": "api"}` and `{"outside": true, "root-need": "clock", ...}` for the world outside the project.
- `via` lists how the connection came about, if not by an explicit line: `"passed up by name"`. `config` is the name of the alternative, or `null`.
- `contract` and `verified-by` are URLs, or paths relative to the root. Both sides of a connection name the same contract, so an entry under `used-by` or `provided-by` repeats none.
- A `status` other than `active`, and a decision status other than `accepted`, means: not in force. The text output marks these in brackets.

## capability

```json
{"unit": "db", "name": "store", "side": "capabilities",
 "ends": [
  {"unit": "db", "status": "planned", "side": "capabilities", "name": "store", "kind": null,
   "summary": "Keeps things", "contract": "schema.sql", "verified-by": null,
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

`distance` 1 is a direct user; higher numbers depend on a dependent. `exposed-as` lists the units above that offer the capability as their own; `outside` the capabilities of the root through which the world uses it directly; `root-capabilities-affected` every capability of the root that depends on it. `stamp` is `current`, `stale` or `missing`.

## tree, deps, cited-by, skills, rules

`tree` prints a list, the root first:

```json
[{"path": "cloud", "name": "cloud", "depth": 1, "status": "planned", "kind": "system",
  "summary": "...", "parent": ".", "capabilities": ["public-api"],
  "needs": ["push-service"], "children": ["cloud/platform"], "nested-projects": []}]
```

`deps` prints the list of [tool.md](tool.md): `[{"from": "crates/printer", "to": "crates/matcher", "kind": "cargo", "evidence": "crates/printer/Cargo.toml [dependencies] grep-matcher"}]`.

`cited-by` prints the `citations` rows of `impact`; a row of kind `link` has no `title`, `says` or `stamp`. `skills` prints `[{"name", "unit", "path", "description"}]`. `rules` prints `[{"id", "severity", "what", "fix", "url"}]`.

## Commands that write

`init`: `{"ok": true, "root", "written": [paths], "notes": [text], "units": 1}`; `written` holds the root manifest, if `init` wrote it, and the generated files. `generate` and `skills sync`: `{"ok", "written", "removed", "refused"}`. `site`: `{"ok": true, "written": "/abs/unifold.html"}`. `stamp` names every stamp it wrote; `action` is `added` or `refreshed`:

```json
{"ok": true, "stamped": 1, "items": [
  {"file": "web/docs/explanation/context.md", "line": 12, "cites": "db/README.md",
   "title": "db: storage rules", "action": "refreshed"}]}
```

## MCP

`unifold mcp` answers `initialize`, `ping`, `tools/list` and `tools/call` as JSON-RPC 2.0, one message per line. A tool result carries the JSON of the command twice: as text in `content[0].text` and as `structuredContent`; the list of `tree` is wrapped as `{"units": [...]}`. A command that fails gives a result with `"isError": true` and the failure object above; an unknown tool gives error `-32602`, an unknown method `-32601`.

| Tool | Arguments |
|---|---|
| `show` | `path` |
| `capability` | `path`, `name` (required) |
| `impact` | `path`, `capability` |
| `check` | `path`, `no_deps` |
| `tree` | `path`, `depth` |

`path` is relative to the folder the server was started for.
