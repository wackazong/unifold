# alerts

Kind: query

```wit
alerts: func(plant-id: option<string>) -> list<alert>;
observe-alerts: func(plant-id: option<string>, observer: alerts-observer);
```

Pre: the store is usable.
Result: open alerts, and alerts closed within the last 90 days, newest first; exactly the alerts the server sent at the last exchange, in the form the public API defines.
Errors: `no session`, `store unusable`.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| after an exchange | the server sent one open alert for "Monstera" | `alerts(none)` | one alert, open |
| never exchanged | the session was started and no exchange succeeded yet | `alerts(none)` | no alerts |
