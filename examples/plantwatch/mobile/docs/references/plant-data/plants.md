# plants

Kind: query

```wit
plants: func() -> list<plant-view>;
observe-plants: func(observer: plants-observer);
```

Pre: the session is not `none`; the store is usable.
Result: every plant, each with its newest reading or none, its open alerts and the age of its readings. Plants with an open alert come first, then by name. "get" answers within 100 milliseconds and never uses the network.
Errors: `no session`, `store unusable`.
Examples:

| Case | Given | Expected |
|---|---|---|
| offline read | no network connection; "get plants" | the plant with its newest reading, within 100 milliseconds |
| reading taken in | a batch of 96 readings is stored; no exchange yet | "readings waiting" is 96, and the plant shows the newest of them |
