# Conventions of store

How work on the log is done. What must hold at every moment is in
[invariants.md](../explanation/invariants.md).

- Compare sequence numbers only with "higher than". They are not consecutive.
- Test every write sequence with a `flash` substitute that cuts power after each single word. Recovery must succeed after every cut. The substitute has to pass the examples in [flash](../../../docs/references/flash.md) itself.
- A change to the [flash layout](flash-layout.md) gets a new layout version. Recovery either still reads the previous version or the change states plainly that stored readings are lost on update.
