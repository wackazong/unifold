# remove-plant

Kind: command

```wit
remove-plant: func(plant-id: string) -> result<_, command-failure>;
```

Pre: the plant is on the phone.
Result: the plant, its alerts and its history are gone from the queries when the command returns; the removal reaches the server without further calls.
Errors: `no session`, `unknown plant`, `store unusable`.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| remove | | `remove-plant` of "Monstera" | ok; `plants()` is empty when the command returns |
| unknown | | `remove-plant` with an id that is not on the phone | `unknown plant` |
