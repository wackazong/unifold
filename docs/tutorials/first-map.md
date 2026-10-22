# Your first map

For a developer who has a repository with a few folders and Python 3.9 or newer. In about fifteen minutes you give the repository a root manifest, describe two folders as units, connect them, and see the first generated diagram. The example is a repository with a folder `billing/` that uses a folder `platform/`; use your own folders in their place.

## 1. Start the project

Run, in the root of the repository:

```sh
uvx unifold init
uvx unifold check
```

`init` writes `unifold.yaml` with the version of the standard, the name of the folder and `summary: TODO`. If the repository has no `README.md`, it writes one from the template: the sections every unit's front page has, with placeholders in angle brackets. `check` prints warnings, the `TODO` and the placeholders, and no error. A project of one unit already conforms.

Replace the `TODO` with one line that says what the repository is. Fill the README's first paragraph and its `## Why`.

## 2. Make one folder a unit

Give the folder that others depend on most a manifest:

```yaml
# platform/unifold.yaml
summary: Shared runtime services
capabilities:
  clock: The current time
```

Run `check` again. It now lists two units and reports nothing new: a capability that nobody uses is only a warning once the parent has other children. Open the root folder: `docs/diagrams/component.md` has appeared, with one box.

## 3. Declare what the second folder needs

Give the second folder a manifest with a need:

```yaml
# billing/unifold.yaml
summary: Creates invoices
needs:
  clock: A time source
```

Write the need in the words of `billing`: what it needs, never who has it. Run `check`. You see an error:

```text
error W2 unifold.yaml:1: need 'billing.clock' has no provider
```

That is the point of the check: a need that nobody meets is found before anybody reads the code.

## 4. Write down what they agree on

Write `docs/references/clock.md` in the root: a few lines on what the clock gives and in which form. A connection carries something, here a time. Its definition is a document that both sides name, and it lives in the unit that will connect them: the root. Name the document in both manifests:

```yaml
# platform/unifold.yaml
capabilities:
  clock: {summary: The current time, contract: ../docs/references/clock.md}
# billing/unifold.yaml
needs:
  clock: {summary: A time source, contract: ../docs/references/clock.md}
```

Without this, the next step ends in an error: a side of a connection that names no contract, or two sides that name different documents.

## 5. Connect the need in the parent

Connect the need in the unit above both folders, here the root:

```yaml
# unifold.yaml in the root
unifold: "0.1"
name: shop
summary: Shop backend
wiring:
  billing.clock: platform.clock
```

Run `check --fix`, then `check`. No error. The component diagram now shows two boxes and an arrow from `billing` to `platform`. If your build files show that `billing` depends on `platform`, the check also confirms that the wiring and the code agree. If the code depends on a folder you have not wired, the check says so, with the file where it found the dependency.

## 6. Ask the map a question

Run:

```sh
uvx unifold show billing
```

It prints the unit, its need, and who finally provides it. From any file inside `billing/` the same command finds the unit. This is what a coding agent runs first.

## 7. Give each unit its README

Write the `README.md` of `platform` from the template of the `unifold` skill; `check` asks every unit for one. It has one paragraph on what the unit is for and a `## Why` of a few lines. Its section for `clock` says what a user can rely on. Do the same for `billing` and the root.

Run `check --fix`. It writes an `AGENTS.md` into each unit, the generated pointer for agents, and `check` is green.

## 8. Let agents in

Run:

```sh
uvx unifold init --agents
```

This installs the skills `unifold` and `unifold-convert` into `docs/skills/`, writes their stubs where agents look, and adds the unifold block to the root `AGENTS.md`. From here, ask an agent to convert the rest of the repository with the skill `unifold-convert`. Or continue one folder at a time: give the next folder a manifest, declare its needs, write the contract, wire them, run `check`. Where code depends on a folder that is not a unit yet, the check reports it; those findings are the list of work that remains. Most folders never need a manifest.
