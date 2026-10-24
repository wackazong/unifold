# <folder-name>

<One paragraph: what this unit is, what it is for, and for whom. A reader who knows nothing else about the project must be able to decide from it whether this is the unit they are looking for. Say what the unit does, not how.>

## Why

<Why this unit exists and why it is cut this way: the forces that shaped it, the main trade-off, what must stay true. Write the reasons a newcomer cannot guess. At most 20 lines that are not blank; the long form is docs/explanation/reasoning.md. No list of children, capabilities or connections: the manifest holds them and `unifold show` prints them.>

## Capabilities

<One `###` section for each capability whose summary and contract do not say everything. Delete the others, and the whole section if none is left.>

### `<capability-name>`

<Only what the contract does not say: what this unit adds beyond it, each guarantee in a form a test could check, and its own limits. Do not repeat the contract; the manifest names it.>

## Needs

<One `###` section for each need whose summary and contract do not say everything. Delete the others, and the whole section if none is left.>

### `<need-name>`

<Only what the contract does not say: what this unit expects beyond it, never who supplies it. For an optional need: what the unit does without it.>

## Out of scope

- <What this unit deliberately does not do, so that nobody asks for it here.>

## Commands

<!-- Optional: the few commands to build, test and run this unit. Delete the section otherwise. -->

## Read next

<!-- Optional: a few links into docs/ whose order matters. Delete the section otherwise. -->
