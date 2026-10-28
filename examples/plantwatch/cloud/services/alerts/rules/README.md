# rules

`rules` is a library that judges readings. Given one reading of a sensor stick and what it concluded from the earlier readings of that sensor stick, it says which alerts open and which close. It asks for the plant and its thresholds through a function it is given. It stores nothing; what it must remember, it returns to its caller.

## Why

When an alert opens and closes is the part of the product that owners feel and that changes most. This unit holds exactly that logic and nothing else, so that it can be read in one sitting and tested with a table of readings and expected alerts. It changes when the rules of judging change: a new quantity, a different margin, another way to look at light.

To stay testable it has no state and knows no technology. What it concluded from earlier readings travels in a value that the caller keeps. Plant and thresholds come through a need whose contract the provider names too; a test meets that need with a table ([context](docs/explanation/context.md)).

An alert must not flap when a value hovers at its threshold, and it must not wait when a plant runs dry. Both are met by opening at the threshold and closing only beyond a margin ([0001](docs/decisions/0001-flapping-is-prevented-by-a-margin-on-closing.md)).

Light shows why judging needs memory: a reading at night is dark for every plant, so light is judged by the brightest reading of a day.

What must stay true: the function is deterministic, and it never asks to open what is open.

## Read next

1. [evaluation](../docs/references/evaluation.md): the function, the rules, the margins, the state
2. [thresholds lookup](../docs/references/thresholds.md): the lookup that the unit expects to be given
3. [docs/explanation/context.md](docs/explanation/context.md): what the unit inherits
4. [Context diagram](docs/diagrams/context.md), [decisions](docs/decisions/index.md)
