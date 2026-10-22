# Invariants of plantwatch

What is true at every moment, in every part. Invariants that the parts must obey are also recorded as decisions or in the [conventions](../references/conventions.md), so that the parts can cite them.

- A reading that has been taken is never changed, at any place.
- A reading is deleted from a place only after the next place has confirmed that it has it.
- Exactly one part talks to both a sensor stick and the server: the phone app.
- No part other than the server side decides whether a plant needs attention. The phone app shows what the server decided ([0006](../decisions/0006-the-server-side-alone-decides-what-needs-attention.md)).
- Within one major version of the radio protocol, a newer part works with an older counterpart.
