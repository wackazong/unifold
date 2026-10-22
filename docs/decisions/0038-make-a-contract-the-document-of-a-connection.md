---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Make a contract the document of a connection, and never a unit

## Context and Problem Statement

The large example had a unit `protocol` that held two specifications and no code. Seven needs in nine manifests were wired to it, and a capability said `conforms-to` a need to mean "I implement that document". Three things were wrong with it. A connection records a dependency that the checker compares with code, and no code depends on a prose folder, so those connections could never be confirmed. Every relationship was doubled: the phone app needed the sensor stick and, as a second need, the description of the sensor stick. And the standard contradicted itself: the documents chapter put a shared definition in the references of the parent, the wiring chapter made it a unit.

Two smaller gaps belonged to the same question. A wiring line could name a plain folder as provider, so a connection did not always join two units. And a `contract` could point anywhere in the project, so a need could name a file of its provider, which is naming the provider.

## Considered Options

- Keep specification units, and make `conforms-to` point at them
- A contract on each side of a connection, optional, compared with a warning
- A contract on each side of every connection, required, equal, or the wiring is invalid; a unit is a unit of processing; a connection always joins two units

## Decision Outcome

Chosen option: "required, equal, two units", because one rule without exceptions is what people and agents can predict: a connection carries something, the document that defines it is its contract, and both sides name that document.

- A unit SHOULD hold code that is built, run or deployed. A specification, a format or a document is never a unit; "a format" leaves the term Capability.
- Every side of a connection names a `contract`, and both sides name the same document; the checker reports anything else as an error. A fragment behind `#` does not count.
- A path in `contract` or `verified-by` lies in the own unit, a unit above it or a unit below it, never in a sibling. So the document of a connection between siblings lives in the references of the unit that wires them, or higher; a chain that no sibling uses may keep it in the implementing child.
- A hand-written file of a unit may link to a file that its manifest names as `contract` or `verified-by`, wherever it lies. This is the one exception to the link rule.
- `conforms-to` is removed. A capability that implements a shared definition names that definition as its contract.
- The folder provider (`child.need: ./folder` and `./`) is removed. A child that depends on code of an ancestor that lies in no unit is reported until that code gets a manifest.

This replaces the home of a contract in 0012, the key `conforms-to` of 0016, the folder line of 0025 and the path rule of 0030. The rest of those decisions stands: both README levels describe a delegated capability, context items keep their form, dependencies are compared with code, and `verified-by` is never demanded.

### Consequences

- Good: a protocol has one home, every implementer names it, and drift between the sides is an error, not a review question.
- Good: no connection is invisible to the comparison with code, and the diagrams show only units that run.
- Good: fewer keys and forms: no `conforms-to`, no folder provider.
- Bad: the definition of a child's interface can live above the child. A child copied elsewhere loses it, and a reader of the child reaches it through the manifest and the generated context page.
- Bad: level `core` is no longer manifests only. The first map costs three manifests and one document. Decision 0030 found that a pointer that must be present attracts whatever passes; a URL contract is checked for its form only.
- Bad: a dependency on code without a manifest is an error from the first run, not a note of work that remains.
