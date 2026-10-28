---
status: superseded by 0073
date: 2026-10-24
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Publish the resolved map as a model with a schema

## Context and Problem Statement

Other tools could build on the map: an extension of an editor, a portal, a linter of a language, the exporters of [0059](0059-export-the-map-to-structurizr-backstage-and-graphviz.md), and agents. Today they have two ways in, and neither is good. They can parse the manifests and implement section 3 of [spec.md](../references/spec.md) again: alternatives, needs passed up, needs met inside, final providers. Or they can read the JSON of single commands ([tool-json.md](../references/tool-json.md)), which serves the commands: `show` gives one unit, `check` gives findings. That JSON belongs to the reference tool and changes with it.

Resolution is the difficult part of the standard. Two implementations that resolve a need differently draw different diagrams from the same manifests. `tests/conformance.py` compares findings and generated files, and it cannot compare a resolution directly.

## Considered Options

- Leave it to tool-json.md
- A command `unifold model` with a schema served beside the schema of the manifest, binding on every tool that writes it
- Make the model a required output of every conforming checker

## Decision Outcome

Chosen option: "a command with a schema that binds every tool that writes it", because it gives others one stable format without asking every checker to write one.

```json
{"unifold-model": "0.3", "project": "shop",
 "units": [
  {"path": "billing", "name": "billing", "summary": "Creates invoices",
   "kind": null, "status": "active", "owner": null, "parent": ".", "children": [],
   "capabilities": [{"name": "invoices", "summary": "Create and fetch invoices",
                     "kind": "http", "contract": "billing/openapi.yaml", "verified-by": null}],
   "needs": [{"name": "clock", "summary": "A time source", "optional": false,
              "contract": "docs/references/clock.md", "contract-taken": false}],
   "x": {}}],
 "connections": [
  {"holder": ".", "key": "billing.clock", "value": "platform.clock",
   "user": "billing", "need": "clock", "provider": "platform", "capability": "clock",
   "alternative": null, "contract": "docs/references/clock.md"}],
 "final": [
  {"user": "billing", "need": "clock", "provider": "platform", "capability": "clock",
   "alternative": null, "outside": false}]}
```

- `unifold model [PATH]` prints the model of the project that contains `PATH`. Paths are relative to the root, which is `"."`.
- `units` holds every unit with what its manifest states. `contract-taken` is `true` when a need takes the contract of its provider ([0052](0052-let-a-wired-need-take-the-contract-of-its-provider.md)). Keys that start with `x-` are carried under `x`, so that a project can attach its own data.
- `connections` holds every wiring line as written, one row per alternative. `final` holds, for every need of every unit, its final provider by rule 7 of section 3. A need that the project does not meet has `"outside": true`.
- The schema is served at `https://unifold.md/0.3/model.schema.json` and follows the version of the standard. A field, once published, keeps its meaning within a version.
- A tool that writes a model MUST follow the schema. A checker does not have to write one.
- `tests/conformance.py` gets cases that compare the model, so that a second implementation is tested on resolution and not only on findings ([tool.md](../references/tool.md) says how to test another implementation).
- The reference tool builds its diagrams and its commands `show`, `capability` and `impact` from the model. Their output does not change.
- The model is not a generated file of section 6. It is never written into the tree by the standard, and nothing checks it.

### Consequences

- Good: other tools use the resolution without implementing it again.
- Good: a second checker can prove that it resolves as the reference does.
- Good: exporters and agents read one format.
- Bad: a second schema to version and keep stable, and every field becomes a promise.
- Bad: readers may take the model for the source. It is derived from the manifests, which stay the only source.
