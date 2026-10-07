# Design principles behind the rules

youmedoc is a way to write things down. It is also a set of opinions about
where boundaries go. This chapter names the established design ideas the rules
come from, so that a reader who knows them can predict the rules, and a reader
who follows the rules arrives at a sound structure.

## Ports and adapters (hexagonal architecture)

| Idea | In youmedoc |
|---|---|
| Driving port: what the application offers | A provided port (`provides`). For events and callbacks the provider starts the conversation; the port is still what the unit offers. |
| Driven port: what the application requires, in its own terms | A need (`needs`). The need belongs to the unit that has it. |
| The application defines its driven ports | A need MAY carry its own `contract`: the interface the unit expects, written by the unit ([manifest.md](manifest.md)) |
| Adapter: translates between a port and a technology | A unit that needs one thing and provides another, usually of a different `kind` |
| Composition root: the place that plugs adapters into ports | The `wiring` of the parent |
| Test double | A second provider for the same need, as a named alternative ([wiring.md](wiring.md)) |
| Two adapters for one port | Provided ports that say `conforms-to` the same definition |

Consequences for design:

- **The core does not know the technology.** A unit that holds rules of the
  domain has needs of kind `library` or `specification`, named in the words of
  the domain. If such a unit needs something that lives behind a network or a
  device, an adapter unit stands between them.
- **When the kinds differ, add an adapter.** A warning that a need of kind
  `library` is wired to a provider of kind `http` (`W4`) is not fixed by
  changing the kind of the need. It shows a missing adapter.
- **A stand-in is a provider like any other.** An emulator, a fake or an
  in-memory store is a unit that provides the same port. The wiring names it
  as an alternative.

## Domain-driven design

| Idea | In youmedoc |
|---|---|
| Bounded context | A unit that has its own glossary, usually near the top of the tree. Not every unit is one. Inside it, each term has one meaning. |
| Ubiquitous language | The glossary of the unit, `doc/references/glossary.md`. A term is defined in the lowest unit that covers all its uses. The nearest glossary wins. |
| Context map | The generated diagrams. The wiring is the list of relationships. |
| Published language, open host service | A provided port with a `contract`; for a language shared by many, a unit of kind `specification` |
| Shared kernel | A unit that owns the shared definition and is needed by all who share it |
| Customer and supplier | A need with its own `contract`: the consumer states what it requires, the provider is held to it |
| Conformist | A need without a contract of its own that says "as the provider defines" |
| Anticorruption layer | An adapter unit, or the consumer's own translation behind a need stated in the consumer's words |
| Domain event | A provided port of kind `events`, with a contract that states key, order and delivery |

Two units may use the same word differently. Then each defines it in its own
glossary, and a unit that receives the other's data says in its `README.md`
how it translates.

## SOLID

| Principle | Rule that carries it | Checked by |
|---|---|---|
| Single responsibility: one reason to change | `AGENTS.md` states the one reason the unit exists and what makes it change; a unit that needs "and" to say it is split | Review rule `C14` |
| Open for extension, closed for modification | New behaviour arrives as a new unit or a new provider; the wiring changes, the consumers do not | The direction rules |
| Substitution | Every alternative provider of a need meets everything the need expects | Review rule `C13` |
| Interface segregation | Ports are narrow. A unit offers several small ports instead of one that every user depends on in full | Review rule `C14` |
| Dependency inversion | A unit depends on its needs, which it states itself; it never names a provider | Tool rules `W1`, `L4`, `L6`; review rules `C2`, `C12` |
| Acyclic dependencies | Children of one unit do not need each other in a cycle | Tool rule `W7` |

## Test-first design

Writing the documents before the code is writing the specification before the
implementation. The same discipline applies one step further: write the check
before the thing it checks.

- **A promise is checkable.** A guarantee in a `README.md` names something
  that can be observed: a value, a limit, an order, a response. "Fast" is not
  a guarantee; "answers within 200 ms for a batch of 500" is.
- **A contract contains examples.** A table of concrete cases, inputs with
  expected results, is the most precise prose there is, and it becomes the
  first test. Put it in the contract reference.
- **A port says what verifies it.** `verified-by` in the manifest points to
  the tests, or to the catalogue of checks, that hold the unit to the port's
  contract.
- **Active means verified.** A unit moves from `planned` to `active` when the
  code exists and the checks named by `verified-by` pass.
- **Consumer first.** When a need has a contract, the provider is tested
  against its cases. The provider does not know its consumers by name; its
  generated context file lists the contracts of the needs it serves, and the
  unit that holds the wiring is responsible for the match.

The order of work is: example in the contract, failing test, code, `active`.
See [workflow.md](workflow.md).

## Small steps

The standard does not ask for the whole tree to be designed before any code
is written. Design the root and the first level, then take one thin slice
through the system to `active` before widening. Documents of `planned` units
are hypotheses; the first running slice corrects them.

## What the principles do not decide

They do not say how big a unit is, how deep the tree goes, or which folder is
a unit. That stays a judgement, guided by "When to make a folder a unit" in
[concepts.md](concepts.md). A project MAY add checks of its own, for example
"a unit of kind `domain` has no need of kind `http`", as rules with IDs that
start with `X` ([rules.md](rules.md)).
