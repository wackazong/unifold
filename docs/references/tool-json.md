# JSON output of the reference tool

Every command of the [tool](tool.md) accepts `--json` and then prints one JSON value on standard output. It holds what the text output holds, under the same names: `show` the unit with the final providers and users of its entries, `capability` both ends of a connection, `impact` the dependents, `tree` the units, `model` the whole resolved map, `rules` the rule table. Paths are relative to the project root, with forward slashes; the root itself is `"."`. A version of the tool may add keys; a reader ignores the keys it does not know. A `status` other than `active`, and a decision status other than `accepted` or `derived`, means: not in force.

Two shapes are fixed, because builds and agents act on them: the failure of a command, and the findings of `check`.

## Failure

When a command cannot run, it prints this object, a message on standard error, and exits with 2 (3 for an internal error):

```json
{"ok": false, "error": {"code": "no-project", "message": "no unifold project found: ..."}}
```

| `code` | Meaning |
|---|---|
| `usage` | Wrong command line |
| `no-project` | No `unifold.yaml` with the key `unifold` here or above |
| `bad-root` | The root manifest does not parse or states another version than 0.4; `check` reports it as a finding instead |
| `no-such-path`, `not-a-folder`, `not-a-root` | The path given does not fit the command |
| `unknown-capability`, `unknown-scenario`, `unknown-rule`, `nested-project` | The thing asked for does not exist here |
| `not-writable`, `io`, `no-mermaid` | A file could not be read or written |
| `internal` | A bug in the tool |

For `check`, the object also has `summary` and an empty `findings` list.

## check

```json
{"ok": false,
 "summary": {"units": 12, "error": 1, "warn": 0, "info": 0, "rules": {"W2": 1},
             "ignored": {"C2": 3}, "root": "/work/shop", "tool": "0.4.0"},
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
- With `--fix`, `summary.fixed` has `written`, `removed` and `refused` (lists of paths). `--fix` writes generated files only.
- `--format github` prints the same findings as lines `::error file=cloud/unifold.yaml,line=14,title=unifold W2::message Fix: ...`, with paths relative to the current folder, then the summary line.

## brief and trace

`brief` prints `{"unit", "name", "responsibility", "kind", "status", "not", "readme", "capabilities", "needs", "scenarios", "constants", "context"}`. A capability has `name`, `summary`, `implemented-by` and `contract`; a need has `name`, `summary`, `optional`, `parts-used`, `provided-by` and `contract`. A `contract` is `{"path", "parts", "states", "fake", "fake-text"}`, and a part `{"name", "kind", "signature", "pre", "result", "errors", "examples"}` with each example `{"id", "case", "given", "input", "expected"}`.

`trace` prints `{"unit", "examples": [{"id", "contract", "part", "case", "line", "tests"}], "unknown": [{"file", "line", "id"}], "findings", "summary": {"examples", "tested", "untested", "unknown"}}`. A finding has the shape of a finding of `check`, with the rules `X1` and `X2`.
