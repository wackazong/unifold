# plant

Kind: query

```wit
plant: func(plant-id: string) -> result<plant-view, query-failure>;
observe-plant: func(plant-id: string, observer: plant-observer);
```

Pre: the session is not `none`; the store is usable.
Result: the plant with its newest reading or none, its open alerts, the age of its readings, its change state and, when the state is `refused`, the reason.
Errors: `unknown plant`, `no session`, `store unusable`.
Examples:

| Case | Given | Expected |
|---|---|---|
| after an offline change | the lower limit of soil moisture was set to 25 without a network | "get plant" shows 25 and `waiting` |
| unknown | a plant id that is not on the phone | `unknown plant` |
