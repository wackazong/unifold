# Your first map

For a developer who has a repository with a few folders, Python 3.9 or newer and [uv](https://docs.astral.sh/uv/). In about fifteen minutes you give the repository a root manifest, describe two folders as units, connect them, and see the first generated diagram. The example is a repository `shop` with a folder `billing/` that uses a folder `platform/`; use your own folders in their place.

The tool is not published as a package yet. Until it is, run it from a clone of the unifold repository: `uv run <clone>/docs/skills/unifold/scripts/unifold.py`. The steps below write `unifold` for that command.

## 1. Start the project

Run, in the root of the repository:

```sh
unifold init
unifold check
```

`init` writes `unifold.yaml` with the version of the standard, the name of the folder and `summary: TODO`. If the repository has no `README.md`, it writes one from the template, with placeholders in angle brackets. `check` prints three warnings and no error: the `TODO`, and two example headings of the template. A project of one unit already conforms.

Replace the `TODO` with one line that says what the repository is. In `README.md`, write the first paragraph and the `## Why`, and delete the sections that do not apply yet. Run `unifold check --fix`. It reports no error and no warning.

## 2. Make one folder a unit

Give the folder that others depend on most a manifest and a front page:

```yaml
# platform/unifold.yaml
summary: Shared runtime services
capabilities:
  clock: The current time
```

```markdown
# platform

Shared runtime services for the other parts of the shop.

## Why

Every part needs the same few services; one implementation keeps them alike.
```

Save the second file as `platform/README.md`; every unit has one. Run `unifold check --fix`. It writes the generated files: `docs/diagrams/component.md` in the root, with one box, and `platform/AGENTS.md`. One warning remains: `'platform.clock' is provided but nothing uses it`.

## 3. Declare what the second folder needs

Give `billing/` a manifest with a need, and a `README.md` like the one of `platform`:

```yaml
# billing/unifold.yaml
summary: Creates invoices
needs:
  clock: A time source
```

Write the need in the words of `billing`: what it needs, never who has it. Run `unifold check --fix`. You see an error:

```text
error W2 unifold.yaml: need 'billing.clock' has no provider
```

That is the point of the check: a need that nobody meets is found before anybody reads the code.

## 4. Connect the need in the parent

Connect the need in the unit above both folders, here the root:

```yaml
# unifold.yaml in the root
unifold: "0.1"
name: shop
summary: Shop backend
wiring:
  billing.clock: platform.clock
```

Run `unifold check --fix`. The first error is gone, and two new ones appear:

```text
error W11 unifold.yaml:5: capability 'platform.clock' names no contract
error W11 unifold.yaml:5: need 'billing.clock' names no contract
```

The connection exists, but nothing says what travels on it.

## 5. Write down what they agree on

Write `docs/references/clock.md` in the root: a few lines on what the clock gives and in which form, with one example. This document is the contract of the connection. It lives in the unit that connects the two sides, and both name it:

```yaml
# platform/unifold.yaml
capabilities:
  clock: {summary: The current time, contract: ../docs/references/clock.md}
# billing/unifold.yaml
needs:
  clock: {summary: A time source, contract: ../docs/references/clock.md}
```

Run `unifold check --fix`. It reports `3 unit(s): 0 error(s), 0 warning(s)`. The component diagram now shows two boxes and an arrow from `billing` to `platform`, labelled `clock`. If your build files show that `billing` depends on `platform`, the check also confirms that the wiring and the code agree. If the code depends on a folder you have not wired, the check says so, with the file where it found the dependency.

## 6. Ask the map a question

Run:

```sh
unifold show billing
```

It prints the unit, its need with the contract, and who provides it: `provided by platform capability 'clock'`. From any file inside `billing/` the same command finds the unit. This is what a coding agent runs first.

## 7. Let agents in

Run:

```sh
unifold init --agents
```

This installs the skills `unifold` and `unifold-convert` and the tool into `docs/skills/`, writes their stubs into `.agents/skills/` and `.claude/skills/`, and adds the unifold block, with the index of units, to the root `AGENTS.md`. From here, ask an agent to convert the rest of the repository with the skill `unifold-convert`. Or continue one folder at a time: a manifest, a `README.md`, the needs, the contract, the wiring line, `check`. Where code depends on a folder that is not a unit yet, the check reports it; those findings are the work that remains. Most folders never need a manifest.
