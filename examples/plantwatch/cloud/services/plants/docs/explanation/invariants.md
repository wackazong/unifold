# Invariants of plants

What is true of the registry and the history at every moment. These lines
keep the history a projection of the events and the registry the one
current truth about a plant.

- An event is handled in one database transaction: the reading, the
  aggregate of its hour and the latest reading of the plant change
  together or not at all. The event is confirmed after the commit.
- No plant and no threshold is cached. Whoever looks up a sensor stick
  gets the current state.
- Every query carries the owner id in its condition. No code path reads a
  plant by id alone, except the lookup by sensor id.
- The field `reading` of an event is stored and returned untouched. Code
  in this unit reads `values`, never `reading`.
