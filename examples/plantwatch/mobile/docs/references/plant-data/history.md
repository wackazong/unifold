# history

Kind: query

```wit
history: func(plant-id: string, from: string, to: string, resolution: resolution) -> result<list<history-entry>, query-failure>;
enum resolution { raw, hourly, daily }
```

Pre: the span reaches back at most 90 days; a `raw` span is at most 7 days long.
Result: the readings of the plant in ascending time: the readings its sensor stick took while it was attached to the plant. With `raw`, one entry per reading. With `hourly`, one entry per hour that has at least one reading; with `daily`, one per day in UTC that has at least one reading; each such entry holds minimum, mean and maximum of each measured quantity, and whether any time in it is estimated.
Errors: `unknown plant`, `no session`, `store unusable`.
Examples:

| Case | Given | Expected |
|---|---|---|
| reading taken in | a batch of 96 readings is stored; no exchange yet | "history" contains the 96 readings |
| hourly | four readings in one hour with soil moisture 41.2, 41.8, 42.1 and 42.5 | one entry: minimum 41.2, mean 41.9, maximum 42.5 |
