# plant

Kind: query

```wit
plant: func(plant-id: string) -> result<plant-view, query-failure>;
observe-plant: func(plant-id: string, observer: plant-observer);
```

Pre: the store is usable.
Result: the plant with its newest reading or none, its open alerts, the age of its readings, its change state and, when the state is `refused`, the [reason](refusal-reason.md).
Errors: `unknown plant`, `no session`, `store unusable`.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| after an offline change | the lower limit of soil moisture was set to 25 without a network | `plant(id)` | 25 and `waiting` |
| unknown | | `plant` with an id that is not on the phone | `unknown plant` |
