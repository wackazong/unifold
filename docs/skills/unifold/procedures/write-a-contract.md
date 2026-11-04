# Write a contract

A contract is the one document of a connection. What each section holds is in <https://unifold.md/contracts>; this procedure gives the order.

1. Write `docs/references/<topic>.md` in the unit that wires the connection, from [contract.template.md](../assets/contract/contract.template.md). State what holds now. Give no reasons; where a decision settled a part, link it.
2. Write the sections in this order: [the header](https://unifold.md/contracts#the-header) with `Notation:`, `Sources:` and, where they apply, `Binding:`, `Carried by:` and `Version:`; [`## Use`](https://unifold.md/contracts#use); [`## States`](https://unifold.md/contracts#states) where the connection has state; [`## Qualities`](https://unifold.md/qualities) where it promises latency, throughput, delivery or limits; [`## Parts`](https://unifold.md/contracts#parts); and [`## Fake`](https://unifold.md/contracts#the-fake). An event has `When:` and `Delivery:`.
3. Give every command and query its examples, in a table `Case | Input | Expected` (or `Case | Given | Input | Expected`): one row per case from the sources, both sides of every precondition, one row per error. Name each case once; its slug is the id of the example, `<contract>#<part>/<case-slug>`, which a test names. They are the first tests of the provider.
4. Define a type once in the subtree; link to it from other contracts.
5. If the contract grows beyond the word limit, make it a folder from [index.template.md](../assets/contract/index.template.md) and [part.template.md](../assets/contract/part.template.md), one file per part.
6. Name the contract from both sides, and list `parts` where a side uses only some.
7. [Finish](../SKILL.md#4-finish). `check` reports what the body of the contract lacks.
