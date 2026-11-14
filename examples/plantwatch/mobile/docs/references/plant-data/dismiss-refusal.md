# dismiss-refusal

Kind: operation

```wit
dismiss-refusal: func(plant-id: string) -> result<_, command-failure>;
```

Pre: the plant is in the state `refused`.
Result: the plant becomes `in step`, with the server's values.
Errors: `no session`, `unknown plant`, `store unusable`.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| dismiss | the plant is `refused` with `sensor stick in use` | `dismiss-refusal(id)` | ok; the plant is `in step` and shows the server's values |
