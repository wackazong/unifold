# Risks of cloud

Risks and known limits of the server side, each with what would remove it.
Planned work is not listed here.

- **The infrastructure is a single point of failure.** The event bus and
  the database run as one instance each. While either is down, uploads are
  refused with `unavailable` and nothing is evaluated
  ([deployment](deployment.md)). Removed by: a second instance of each,
  which version 1 leaves out on purpose
  ([platform](../../platform/README.md)).
- **No proof that an upload comes from the owner of the sensor stick.** A
  sensor stick holds no secret, so any client with a valid token can upload
  readings under any sensor id ([context](context.md)). Removed by: a secret
  on the stick, which is a decision above this unit.
- **Late batches judge the past.** `cloud` judges a reading by the time it
  carries. A batch that arrives days late opens and closes alerts late, and
  the owner is told about a state that may be over. Accepted knowingly; the
  public API states it. Removed by: a rule that does not notify about an
  alert whose reading is older than a limit, which is not decided.
- **Queries lag behind uploads.** A reading reported as `new` appears in
  history within 10 seconds after the upload response, not within the
  request, because history is a separate consumer of events
  ([0001](../decisions/0001-services-learn-about-readings-through-events.md)).
  Removed by: nothing without giving up the independent upload path.
- **Every event can arrive twice.** Every consumer carries its own
  safeguard, and a safeguard that is forgotten in a new consumer doubles an
  effect ([0004](../decisions/0004-every-event-consumer-is-idempotent.md)).
  Removed by: a test of every consumer with each event delivered twice.
