# Your first map

For a developer who has a repository with a few folders and Python 3.9 or
newer. In about fifteen minutes you give the repository a root manifest,
describe two folders as units, connect them, and see the first generated
diagram. The example is a repository with a folder `billing/` that uses a
folder `platform/`; use your own folders in their place.

## 1. Start the project

In the root of the repository:

```sh
uvx unifold init
uvx unifold check
```

`init` writes `unifold.yaml` with the version of the standard, the name of
the folder and `summary: TODO`. `check` prints one warning, the `TODO`, and
no error. A project of one unit already conforms. Replace the `TODO` with
one line that says what the repository is.

## 2. Make one folder a unit

Give the folder that others depend on most a manifest:

```yaml
# platform/unifold.yaml
summary: Shared runtime services
capabilities:
  clock: The current time
```

Run `check` again. It now lists two units and reports nothing new: a
capability that nobody uses is only a warning once the parent has other
children. Open the root folder: `docs/diagrams/component.md` has appeared,
with one box.

## 3. Declare what the second folder needs

```yaml
# billing/unifold.yaml
summary: Creates invoices
needs:
  clock: A time source
```

Write the need in the words of `billing`: what it needs, never who has it.
Run `check`. You see an error:

```text
error W2 unifold.yaml:1: need 'billing.clock' has no provider
```

That is the point of the check: a need that nobody meets is found before
anybody reads the code.

## 4. Connect the need in the parent

The unit above both folders, here the root, connects every need:

```yaml
# unifold.yaml in the root
unifold: "0.1"
name: shop
summary: Shop backend
wiring:
  billing.clock: platform.clock
```

Run `check --fix`, then `check`. No error. The component diagram now shows
two boxes and an arrow from `billing` to `platform`. If your build files
show that `billing` depends on `platform`, the check also confirms that the
wiring and the code agree; if the code depends on a folder you have not
wired, the check says so, with the file where it found the dependency.

## 5. Ask the map a question

```sh
uvx unifold show billing
```

It prints the unit, its need, and who finally provides it. From any file
inside `billing/` the same command finds the unit. This is what a coding
agent runs first.

## 6. Give one unit its documents

Set `level: full` in `platform/unifold.yaml`. `check` now asks for a
`README.md`. Write it from the template of the `unifold` skill: one
paragraph that says what the unit is for, a `## Why` of a few lines, and a
section for `clock` that says what a user can rely on. Run `check --fix`:
it writes `platform/AGENTS.md`, the generated pointer for agents. The rest
of the repository stays at level `core`, and `check` stays green.

## 7. Let agents in

```sh
uvx unifold init --agents
```

This installs the skills `unifold` and `unifold-convert` into
`docs/skills/`, writes their stubs where agents look, and adds the unifold
block to the root `AGENTS.md`. From here, ask an agent to convert the rest
of the repository with the skill `unifold-convert`, or continue one folder
at a time: give the next folder a manifest, declare its needs, wire them
in the parent, run `check`. Where a need is met by code that is not a unit
yet, name the folder: `billing.ledger: ./legacy/ledger`. Those lines are
the list of work that remains. Most folders never need a manifest.
