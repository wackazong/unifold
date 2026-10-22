# Glossary of cloud

The terms that have one fixed meaning inside `cloud` and that the project glossary does not define. The project terms that `cloud` uses are cited in [context](../explanation/context.md).

| Term | Meaning |
|---|---|
| Client | A program that calls the public API for one owner, for example a phone app. |
| Token | The string a client sends to prove for which owner it acts. |
| Service | One deployable program of `cloud` with capabilities and data of its own. |
| Upload | One request that carries a batch. |
| Accepted reading | A reading that an upload reported as `new`. It is announced as an event. |
| Registry | The stored plants with their owners, attached sensor sticks and thresholds. |
| History | The accepted readings of a plant, raw or as aggregates. |
| Aggregate | Minimum, mean and maximum of each quantity over one hour or one day of history. |
| Event | A message by which a service announces a fact to other services. The rules are in [events](events.md). |
| Topic, subscription, key | Where events are published; the position of one consuming service on a topic; the value that orders events. See [events](events.md). |
| Bound | The side of a threshold: `min` or `max`. |
| Judged value | The value that is compared with a threshold: for light the highest of a day, otherwise the value of the reading. |
| Margin | The distance by which a judged value must be back on the good side of a threshold before an alert closes. |
| Collapse identifier | A value sent with a notification. Two notifications with the same value show on a phone as one. |
