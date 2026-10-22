# Reasoning of alerts

The long form of the why in [README.md](../../README.md). Which children exist and how they are wired is shown in the [component diagram](../diagrams/component.md).

**Judging is pure.** Whether a reading opens or closes an alert depends on the reading, the thresholds and what was judged before. It does not depend on a database, a clock or a network. Kept as a library with no state of its own, the judging can be tested with tables of readings and changed without touching storage.

**What lies behind a network gets an adapter.** The registry of plants and the push service are reached over HTTP, can be slow and can fail. Each has an adapter that provides a plain function and hides the rest, including the wording of a notification. The caller and the adapter name the same contract for that function, a reference of this unit ([0003](../decisions/0003-thresholds-reach-the-judging-logic-through-an-adapter.md)).

**One process holds the state and the order.** One child alone stores anything durably and knows in which order things happen. It calls the judging and the notifying; nothing calls it back.

**Libraries, not services.** All parts are deployed as one program ([0001](../decisions/0001-evaluation-and-notification-are-libraries-beside-one-process.md)). An alert, the state that led to it and the fact that its notification is still owed are then written in one database transaction ([0002](../decisions/0002-the-alert-row-is-the-outbox-of-its-notification.md)).

## Trade-offs

| Chosen | Given up | Decision |
|---|---|---|
| A lookup of thresholds stands between an event and its alert | While the lookup answers `unavailable`, events of that sensor stick wait. The alternative, a copy of all thresholds inside `alerts`, is rejected one level up ([context](context.md)). | [0003](../decisions/0003-thresholds-reach-the-judging-logic-through-an-adapter.md) |
| An answer of the registry may be reused for up to 60 seconds | A threshold that was changed takes up to 60 seconds to apply | decided in `plant-lookup` |
| The interface between a caller and its adapter is one more contract of `alerts`, named by both sides | One more unit and one more contract to keep in step | [0003](../decisions/0003-thresholds-reach-the-judging-logic-through-an-adapter.md) |
| Notifications are effectively once, not exactly once | A repeat that reaches a phone after the owner has dismissed the first one is shown again. The window for this is the few seconds between sending and storing. | [0002](../decisions/0002-the-alert-row-is-the-outbox-of-its-notification.md) |
| `alerts` is not told about plants that were deleted or lost their sensor stick | Alerts of such a plant stay open until they expire | none; follows from asking instead of copying |
