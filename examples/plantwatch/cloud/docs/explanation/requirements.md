# Requirements of cloud

`cloud` must turn the readings that clients upload into the history of every plant and into alerts, and tell an owner once when a plant needs attention, while no client is online. It is for clients that act for an owner and for whoever operates the containers. It is not for sensor sticks, which never reach it, and not for a caller without a token.

## Goals

1. **An upload waits for nothing but acceptance.** A batch is accepted while history, evaluation and the push service are down, and the response says for every reading whether it is `new`, `duplicate` or `rejected`.
2. **One notification per alert.** An accepted reading that makes a plant need attention opens one alert and hands one notification to the push service. A repeated upload or a repeated event changes nothing.
3. **History for two years.** Raw readings for 90 days, hourly and daily aggregates for 2 years, per plant.
4. **An owner sees only what is theirs.** A plant or an alert of another owner answers `404`.
5. **Every request is safe to repeat.** The same upload, the same `PUT` and the same query, sent twice, leave the same state.

## Quality goals, in the order in which they win

| Rank | Quality | Observed as |
|---|---|---|
| 1 | Availability of the upload path | An upload succeeds while every service but the one that accepts readings is stopped |
| 2 | Correctness of alerts | At most one open alert per plant, quantity and bound; an event delivered twice opens none |
| 3 | Freshness | An alert and its notification follow the upload response within 1 minute; a reading is in the history within 10 seconds |
| 4 | Isolation of services | No service reads the schema of another; a schema change is a change to one service |
| 5 | Operability | Every service can be stopped and started without losing data, and replaced without a pause in uploads |
