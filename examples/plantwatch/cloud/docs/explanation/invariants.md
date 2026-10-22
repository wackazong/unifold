# Invariants of cloud

What is true at every moment on the server side, across all services. A
change that breaks one of these lines is a decision, not maintenance.

- A reading that an upload reports as new or duplicate is on the event bus
  and reaches every subscriber, also one that is down at that moment.
- An upload calls no service other than the one that accepts readings, and
  no synchronous call is added to its path: an upload succeeds when the
  reading is accepted, whatever else is down.
- No service reads or writes the database schema of another service.
- No container other than the public entry is reachable from outside the
  private network.
- Every event consumer produces the same result when an event arrives twice
  ([0004](../decisions/0004-every-event-consumer-is-idempotent.md)).
- Events of one sensor stick are processed in the order in which their
  readings were accepted.
- Only [alerts](../../services/alerts/README.md) decides that a plant needs
  attention, and only it talks to the push service.
- A change that breaks clients gets a new path prefix in the public API. A
  change that breaks subscribers gets a new topic.
- An interface between two services is defined in this unit, never in one
  of the two. That holds for every event type and every call.
