# Concepts

This chapter defines the terms used by all other chapters of
[youmedoc](index.md).

## Terms

**Project.** A folder tree, normally a repository, whose top folder is a root
unit.

**Unit.** A folder whose `README.md` begins with a manifest that contains the
key `unit`. A unit is a part of the system that has an interface: a library, a
service, an application, a firmware image, a tool, a shared protocol
definition. Being a unit is optional. A folder becomes a unit when someone
needs to understand it without reading its insides.

**Root unit.** The unit at the top of the project. Its manifest also contains
the key `youmedoc` with the version of the standard.

**Plain folder.** Any folder that is not a unit. Plain folders are transparent:
a unit inside a plain folder belongs to the nearest unit above.

**Parent, child, sibling.** The parent of a unit is the nearest unit above it
in the folder tree. Its children are the units for which it is the parent.
Siblings share a parent.

**Manifest.** The YAML front matter of a unit's `README.md`. It names the unit
and declares its ports and its wiring. See [manifest.md](manifest.md).

**Port.** A named point of the unit's interface. There are two sorts:

- A **provided port** is something the unit offers: an API, a protocol, a
  command line, a stream of events, a file format, a user interface.
- A **need** is something the unit requires from outside itself. A need names
  *what* is required, never *who* supplies it.

**Wiring.** The part of a parent's manifest that connects each need to a
provider. The need is the key and the provider is the value. See
[wiring.md](wiring.md).

**Context.** What a unit inherits from the levels above: decisions,
conventions and terms. A unit records it in `doc/context.md`, with a short
restatement of each item. See [doc-folder.md](doc-folder.md).

**Hand-written file.** A file written by an agent or a human. "Hand-written"
means "not produced by the generator".

**Generated file.** A file produced by the generator from the manifests. It
starts with a marker comment and is never edited. See
[diagrams.md](diagrams.md).

**Nested project.** A folder below the root whose manifest also contains
`youmedoc`. It is a separate project. The outer project treats it as a closed
box and may link only to its `README.md`.

## The three principles

### 1. The folder is the unit

Units are folders of the real code layout. youmedoc adds no folders of its own
except `doc/`. If the documentation wants a box that the folder tree does not
have, the folder tree is what needs to change.

Consequences:

- Something shared by several units, such as a protocol definition or a
  schema, is a unit of its own with its own folder. It is not a note in the
  parent.
- A view that cuts across the folder tree, such as a deployment view or a
  sequence of calls, is not part of the declared structure. It may be drawn by
  hand in `doc/architecture.md` of the lowest unit that contains everything it
  shows.

### 2. Knowledge points inward and downward

A unit knows its own insides and the interfaces of its direct children.
It knows nothing else by name.

- It does not know its siblings. What it wants from them is a need.
- It does not know its users.
- It does not know the insides of its children.
- It knows what it inherits from above only through `doc/context.md`.

This is what makes a parent small and a child understandable on its own. The
exact rules are in [rules.md](rules.md).

### 3. Say it once, link everywhere

Every fact has one home. Other files link to it.

Five repetitions are allowed because they keep files usable on their own:

1. the one-line `summary` of a unit or port, which the generator repeats in
   tables,
2. the restatement of an inherited item in `doc/context.md`,
3. a few sentences in `AGENTS.md` that summarise `doc/architecture.md`,
4. an inherited value that is part of the unit's own interface, such as a
   limit or a unit of measure, in the unit's `README.md` or in a contract,
   provided `doc/context.md` cites where it comes from,
5. a port that a unit delegates to a child: both describe it, each at its
   own level ([unit-files.md](unit-files.md)).

## Who writes and who reads

- Agents write most files and keep them consistent.
- Humans read, correct and decide. A decision record written by an agent stays
  `proposed` until a human accepts it.
- Both read the same files. No file exists only for one of them. `AGENTS.md`
  is named after its first reader, but it is written so that a human learns
  from it too.

This is why files are short, why structure is declared in a form a tool can
check, and why everything derivable is generated.

## What a unit is not

- Not every folder. Most folders stay plain.
- Not a layer or a tag. A unit is one folder with one interface.
- Not required to contain code yet. A unit with `status: planned` describes
  code that does not exist.

## When to make a folder a unit

Make a folder a unit when at least one of these holds:

- other parts use it through an interface that should stay stable,
- it is built, deployed, released or tested on its own,
- it has decisions or procedures of its own,
- a reader needs a box for it in a diagram.

Leave it plain when it only groups files or other units and has nothing to say
for itself.
