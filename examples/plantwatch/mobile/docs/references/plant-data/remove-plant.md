# remove-plant

Kind: command

```wit
remove-plant: func(plant-id: string) -> result<_, command-failure>;
```

Pre: the session is `active`; the plant is on the phone.
Result: the plant, its alerts and its history are gone from the queries when the command returns; the removal reaches the server without further calls.
Errors: `no session`, `unknown plant`, `store unusable`.
Examples:

| Case | Given | Expected |
|---|---|---|
| remove | "remove plant" for "Monstera" | "get plants" is empty when the command returns |
| unknown | a plant id that is not on the phone | `unknown plant` |
