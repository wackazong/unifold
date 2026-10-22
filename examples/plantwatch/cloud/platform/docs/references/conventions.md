# Conventions of platform

How work in this unit is done. What must hold at every moment is in the
[invariants](../explanation/invariants.md).

- The two contracts are technology-neutral where a service relies on them and name the product only where a client must know the wire protocol. A feature of the product that is not in the contract is not promised.
- A topic that needs more partitions is replaced by a new topic, because changing the number of partitions of a topic breaks the order within a key.
- A product upgrade that changes a guarantee in a contract is a decision, not maintenance.
