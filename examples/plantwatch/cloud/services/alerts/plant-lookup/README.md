# plant-lookup

`plant-lookup` is an adapter. It answers one question as a plain function call: to which plant is this sensor stick attached, who owns that plant and what are its thresholds. Behind the function it asks the registry of plants over HTTP, repeats a call that failed and keeps an answer for 60 seconds. Its caller needs to know nothing about HTTP, time limits or network errors.

## Why

The logic that judges a reading must not know that thresholds live behind a network. This unit exists to hold that knowledge in one place: the path of the request, the time limit, the repeats, the meaning of each status and how long an answer may be reused. It changes when the way the registry of plants is reached changes, and for no other reason.

It is cut as an adapter with a plain function on one side and HTTP on the other, so that its caller can be tested with a stand-in that returns fixed answers, and so that a different source of thresholds replaces this unit and nothing else.

The one real choice is what to do between asking every time and answering from memory. Answers are kept for at most 60 seconds, and an outage of the registry yields `unavailable` instead of an old answer ([0001](docs/decisions/0001-keep-an-answer-for-at-most-60-seconds.md)). A late alert is better than an alert judged by thresholds that the owner has already changed.

What must stay true: no answer is older than 60 seconds, and no failure reaches the caller as anything but `unavailable`.

## Read next

1. [thresholds lookup](../docs/references/thresholds.md): the function, how answers of the registry are mapped, the kept answers
2. [docs/explanation/context.md](docs/explanation/context.md): what the unit inherits
3. [Context diagram](docs/diagrams/context.md), [decisions](docs/decisions/index.md)
