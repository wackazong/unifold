# plants

Kind: operation

```wit
plants: func() -> result<list<plant-view>, command-failure>;
observe-plants: func(observer: plants-observer);
```

Pre: the store is usable.
Result: every plant, each with its newest reading or none, its open alerts and the age of its readings. Plants with an open alert come first, then by name.
Errors: `no session`, `store unusable`.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| offline read | no network connection | `plants()` | the plant with its newest reading, within 100 milliseconds |
| reading taken in | a batch of 96 readings is stored; no exchange yet | `plants()` | the plant shows the newest of them; `readings-waiting` of the exchange state is 96 |
