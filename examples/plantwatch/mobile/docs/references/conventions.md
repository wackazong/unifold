# Conventions of mobile

How work in the app is done, across all of its parts. What must hold at every moment is in [invariants.md](../explanation/invariants.md).

- What two children exchange is a capability of one of them. Change the capability and the wiring, and record a decision here. Do not let one child reach into another.
- Use the names of the [data model](data-model.md) and of the [glossary](glossary.md) for the things the app handles and does. Do not invent a second word for one of them.
- Background behaviour cannot be judged in a simulator or a debug build. The operating systems treat an installed release build on a real phone differently. Verify every change to background fetching there.
- The limits in [platform-limits.md](platform-limits.md) change with every major release of an operating system. Treat a number from memory as outdated and look it up.
