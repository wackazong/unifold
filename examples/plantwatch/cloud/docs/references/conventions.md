# Conventions of cloud

How work on the server side is done. What must hold at every moment is in
the [invariants](../explanation/invariants.md).

- The [public API](public-api/index.md) is the contract with clients. A
  change is made there first; the services that serve a part of it follow.
- After a change to a child's capability, both ends of every wiring line
  that touches it are read again: the need of one child and the capability
  of the other must still say the same.
- A new measured quantity changes the public API first, then every service
  that validates, stores or evaluates readings. Each of them has a skill
  for its part.
