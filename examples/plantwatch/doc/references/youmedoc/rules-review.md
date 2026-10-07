# Review rules

These rules concern meaning. A tool cannot check them. An agent or a human
checks them by reading. The overview is in [rules.md](rules.md).

For each rule: the statement, how to check it, and the usual fix.

## C1: The README describes the unit as a closed box

`README.md` can be understood without opening another file. It says what
every provided port offers and guarantees and what every need expects. It
says nothing about how the unit works inside.

- **Check:** Read only the `README.md`. Could you use the unit? Could you
  provide what it needs? Does any sentence describe an internal part?
- **Fix:** Add the missing guarantee or expectation. Move internals to
  `AGENTS.md` or `doc/architecture.md`.

## C2: A unit does not know its surroundings

No hand-written file of a unit names its siblings, its parent or its users,
with the exception of `doc/context.md`, which may name ancestors.

- **Check:** Search the unit's files for the names of sibling and ancestor
  units and for phrases such as "used by" and "called from". What counts is
  a reference to the unit. The same word used in its everyday sense, the
  name of the product, a title quoted in `doc/context.md`, and the names of
  the standard's skills do not count.
- **Fix:** Replace the mention by the need or the provided port it stands
  for. Write "whoever provides `clock`", not the provider's name.

## C3: A parent describes children only from outside

A unit's files mention a child only by its name, with a link to its
`README.md`. They do not restate the child's ports, guarantees or insides.

- **Check:** For each mention of a child: would the sentence have to change
  if the child changed inside, or changed its interface text? A unit's
  description of its own port is not a restatement, also when the port is
  delegated to a child.
- **Fix:** Cut the restatement and keep the link.

## C4: Structure is not written by hand

`AGENTS.md` and `doc/architecture.md` explain why. They contain no list of
child units, no list of ports and no description of who is wired to whom.

- **Check:** Look for lists, tables or hand-drawn diagrams that mirror the
  manifest or the generated diagrams. Naming children in reasoning, and
  tables that add what the manifest does not say, are fine.
- **Fix:** Delete them and link to the diagram. Keep the sentence that says
  why the structure is as it is.

## C5: Context is cited completely and only where it matters

Every item in `doc/context.md` has a link, a restatement and a consequence
for this unit. The unit cites everything it relies on from above and nothing
else.

- **Check:** Read the unit's files. Does any statement depend on a rule,
  decision or term that is defined above and not cited? Is any cited item
  without effect here? Does each restatement still match its source?
- **Fix:** Add, remove or correct the citation.

## C6: Every fact has one home

A fact is stated in full in one file. Other files link to it. Allowed
repetitions are listed in [concepts.md](concepts.md).

- **Check:** For each paragraph of a changed file, ask whether the same
  content exists elsewhere in the project.
- **Fix:** Keep the copy in the file where [unit-files.md](unit-files.md)
  says it belongs and replace the other by a link.

## C7: Decisions are honest records

An accepted decision is not edited apart from its status. A decision written
by an agent is `proposed` until a human accepts it. A decision that no longer
holds is marked `deprecated` or `superseded by NNNN`.

- **Check:** Compare changed decision files with version control. Check that
  every decision the unit's files rely on has a status that allows it.
- **Fix:** Restore the old text and add a new decision that supersedes it.

## C8: Decisions, references and skills sit at the right level

Each of them belongs to the lowest unit whose insides it fully covers. A
decision about the interface between siblings belongs to their parent.

- **Check:** Does the item speak about more than this unit? Then it is too
  low. Does it speak only about one child? Then it is too high.
- **Fix:** Move the file. A child that depends on it cites it in
  `doc/context.md`.

## C9: Each file contains its own sort of content

Reasons are in decisions and in the why. Facts are in references. Procedures
for whoever works on the unit are in skills. Interfaces are in the
`README.md`.

- **Check:** Look for work instructions in references, for reasons in
  skills, for facts buried in decisions that readers will look up later. The
  steps of a protocol or of a process of the system are facts.
- **Fix:** Move the content and link to it.

## C10: The documents match reality

The manifest, the `status` and the texts describe the unit as it is, or, for
a `planned` unit, as it is intended.

- **Check:** Where code exists, compare the provided ports with what the code
  exposes and the needs with what the code uses. Check that `status` is right
  and that `contract` points to the most precise description that exists.
- **Fix:** Change the documents, or report that the code deviates. Do not
  silently adapt the documents to an accidental state of the code.

## C11: Units follow the code layout

Every unit is a folder of the real code layout with an interface of its own.
No folder exists only for documentation, apart from `doc/`.

- **Check:** For each unit: is there, or will there be, code or deployable
  content in this folder? Does the folder boundary match a boundary in the
  build or deployment?
- **Fix:** Merge the unit into its parent, or change the code layout.

## C12: Names are stable and meaningful

Unit and port names say what the thing is, not who uses it or how it is
implemented. A need is named after what is needed.

- **Check:** Does a need carry the name of its current provider? Does a port
  name contain a technology that might change?
- **Fix:** Rename, and update the wiring in the parent.

## C13: Every need matches its provider

For every line of a unit's wiring, what the need expects is covered by what
the provider's `README.md` offers. For an own need that is passed down, the
unit's description of the need covers what the children expect of it.

- **Check:** In the unit that holds the wiring, read both ends of each line:
  the `## Needs` text of one child and the `## Provides` text of the other.
  Compare guarantees, limits, names of operations and data.
- **Fix:** Change the side that is wrong. If both are defensible, record a
  decision in the unit that holds the wiring.

## Reporting

Report each finding as: rule ID, file, the offending text, the proposed fix.
Example:

```text
C2 device/link/README.md: "the mobile app reconnects after 5 s" names a user.
   Fix: "a central that loses the connection may reconnect after 5 s".
```
