# Review rules

These rules concern meaning. A tool cannot check them. An agent or a human
checks them by reading. The overview is in [rules.md](rules.md). Which rules
apply to which kind of change is listed in the
[check-docs](../../skills/check-docs/SKILL.md) skill.

## C1: The README describes the unit as a closed box

`README.md` can be understood without opening another file. It says what
every provided port offers and guarantees and what every need expects, and
nothing about how the unit works inside.

- **Check:** Read only the `README.md`. Could you use the unit? Could you
  provide what it needs?
- **Fix:** Add the missing guarantee or expectation. Move internals to
  `AGENTS.md` or `doc/architecture.md`.

## C2: A unit does not know its surroundings

No hand-written file of a unit names its siblings, its parent or its users,
except `doc/context.md`, which may name ancestors.

- **Check:** Search for the names of sibling and ancestor units and for
  phrases such as "used by" and "called from". What counts is a reference to
  the unit. The everyday word, the name of the product, a title quoted in
  `doc/context.md` and the names of the standard's skills do not count.
- **Fix:** Replace the mention by the need or port it stands for. Write
  "whoever provides `clock`", not the provider's name.

## C3: A parent describes children only from outside

A unit's files mention a child only by name, with a link to its `README.md`.
They do not restate the child's ports, guarantees or insides. A unit's
description of its own port is not a restatement, also when the port is
delegated.

- **Check:** Would the sentence have to change if the child changed inside?
- **Fix:** Cut the restatement and keep the link.

## C4: Structure is not written by hand

`AGENTS.md` and `doc/architecture.md` explain why. They contain no list of
child units or ports and no description of who is wired to whom. Naming
children in reasoning, and tables that add what the manifest does not say,
are fine.

- **Check:** Look for lists, tables or diagrams that mirror the manifest.
- **Fix:** Delete them, link to the diagram, keep the sentence that says why.

## C5: Context is cited completely, briefly, and only where it matters

Every item in `doc/context.md` has a link, a restatement of about 200 characters
and a consequence for this unit. The unit cites everything it relies on from
above and nothing else. Each restatement matches its source.

- **Check:** Does any statement of the unit depend on something defined
  above that is not cited? Is any item without effect here? After a source
  changed, list its citations with `cited-by` and compare each.
- **Fix:** Add, remove, shorten or correct the citation.

## C6: Every fact has one home

A fact is stated in full in one file. Other files link to it. Allowed
repetitions are listed in [concepts.md](concepts.md).

- **Check:** For each number with a unit, each identifier and each rule in a
  changed paragraph, search the project. Every other occurrence is one of the
  allowed repetitions, or it goes.
- **Fix:** Keep the copy where [unit-files.md](unit-files.md) says it
  belongs and replace the other by a link.

## C7: Decisions are honest records

An accepted decision is not edited apart from its status. A decision written
by an agent is `proposed` until a human accepts it. A decision that no longer
holds is marked `deprecated` or `superseded by NNNN`.

- **Check:** Compare changed decision files with version control. No change
  sets `accepted` unless a human asked for exactly that.
- **Fix:** Restore the old text and add a new decision that supersedes it.

## C8: Decisions, references and skills sit at the right level

Each belongs to the lowest unit whose insides it fully covers. A decision
about the interface between siblings belongs to their parent.

- **Check:** Does the item speak about more than this unit? Then it is too
  low. Only about one child? Then it is too high.
- **Fix:** Move the file. A child that depends on it cites it in
  `doc/context.md`.

## C9: Each file contains its own sort of content

Reasons are in decisions and in the why. Facts are in references. Procedures
for whoever works on the unit are in skills. Interfaces are in the
`README.md`. The steps of a protocol or a process of the system are facts.

- **Check:** Look for work instructions in references, reasons in skills,
  facts buried in decisions.
- **Fix:** Move the content and link to it.

## C10: The documents match reality

The manifest, the `status` and the texts describe the unit as it is, or, for
a `planned` unit, as it is intended. Documents change in the same commit as
the code they describe.

- **Check:** Where code exists, compare the ports with what the code exposes
  and uses. Check that `status` is right and that `contract` and
  `verified-by` point to what exists.
- **Fix:** Change the documents, or report that the code deviates. Do not
  silently adapt the documents to an accidental state of the code.

## C11: Units follow the code layout

Every unit is a folder of the real code layout with an interface of its own.
No folder exists only for documentation, apart from `doc/`.

- **Check:** Is there, or will there be, code or deployable content in this
  folder? Does its boundary match one in the build or deployment?
- **Fix:** Merge the unit into its parent, or change the code layout.

## C12: Names are stable and meaningful

Unit and port names say what the thing is, not who uses it or how it is
implemented. A need is named after what is needed, in the words of the unit
that has it.

- **Check:** Does a need carry the name of the unit that provides it today?
  Does a port name contain a technology that might change? A need named
  after the kind of thing it is, such as `plants-api`, is fine.
- **Fix:** Rename, and update the wiring in the parent.

## C13: Every need matches its provider

For every line of a unit's wiring, what the need expects is covered by what
the provider offers. This holds for every alternative: each one can replace
the others, alone and in its default configuration. If the need has a
contract, the provider meets it.

- **Check:** In the unit that holds the wiring, read both ends of each
  changed line: the `## Needs` text and contract of one child, the
  `## Provides` text and contract of the other. Compare guarantees, limits,
  names of operations and data.
- **Fix:** Change the side that is wrong. If both are defensible, record a
  decision in the unit that holds the wiring.

## C14: One responsibility, narrow ports

A unit has one reason to exist and one kind of reason to change, and
`AGENTS.md` states it. A port offers one coherent thing; a user of a port
depends on all of it.

- **Check:** Does the `summary` need "and" to join unrelated things? Would
  two different kinds of change both land in this unit? Does a typical user
  of a port use only a small part of it?
- **Fix:** Split the unit or the port. Record why in a decision.

## C15: Promises can be checked

Every guarantee in a `README.md` or contract names something observable. A
contract contains examples. For an `active` unit, the checks named by
`verified-by` exist, cover the contract and pass.

- **Check:** For each guarantee: which test would fail if it were broken?
- **Fix:** Make the guarantee concrete, add the example, add the check, or
  set the unit back to `planned`.

## Reporting

Report each finding as: rule ID, file, the offending text, the proposed fix.

```text
C2 device/link/README.md: "the mobile app reconnects after 5 s" names a user.
   Fix: "a central that loses the connection may reconnect after 5 s".
```
