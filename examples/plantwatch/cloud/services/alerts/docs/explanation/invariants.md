# Invariants of alerts

What is true at every moment inside this unit, across its children. The
promise they protect: an alert opens once, and an opened alert leads to one
notification, although events and calls can repeat.

- At most one alert is open per plant, quantity and bound.
- **One notification per opened alert.** Every alert is stored with a
  notification that is owed. The notification is handed to the push
  service at least once and, seen by the owner, once.
- No notification without a stored alert. An alert is committed before
  anything is sent.
- No notification is sent from the handling of an event. Handling stores
  the alert with a pending notification; delivery is a separate step that
  can repeat
  ([0002](../decisions/0002-the-alert-row-is-the-outbox-of-its-notification.md)).
- A reading is judged at most once per sensor stick, and never after a
  newer reading of the same sensor stick was judged.
- A closed alert stays closed.
- Judging uses the time of readings only, never the clock. Handling the
  same events in the same order gives the same alerts on any day.
- The children do not know each other. What one wants from another is a
  need with a contract of its own; only the wiring of this unit connects
  them.
- A need of the judging logic is of kind `library`. Whatever lives behind
  a network gets an adapter.
- Only the process stores anything. A library that must remember something
  between two calls returns it to its caller. The one exception is
  recorded in
  [0003](../decisions/0003-thresholds-reach-the-judging-logic-through-an-adapter.md).

How the children share the work for the notification invariant:

| Danger | What prevents it |
|---|---|
| An event arrives twice and the alert opens twice | The evaluation state says the alert is open; the stored alerts allow one open alert per plant, quantity and bound |
| The process stops after storing the alert and before notifying | The alert is stored as owing a notification; delivery starts again from the stored alerts |
| The process stops after the push service took the notification and before that is stored | The alert is notified again; [notifier](../../notifier/README.md) makes a repeat for the same alert harmless |
| The push service is down | The notification stays owed and is tried again for 24 hours |
