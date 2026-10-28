# refusal-reason

Kind: type

```wit
variant refusal-reason { removed-elsewhere, sensor-stick-in-use, limit-reached, not-accepted(string) }
```

| Reason | Meaning |
|---|---|
| `removed elsewhere` | the plant no longer exists on the server; it disappears from the phone as well |
| `sensor stick in use` | the server knows the sensor stick as attached to another plant |
| `limit reached` | the owner has 50 plants on the server |
| `not accepted` | any other refusal; with the message the server gave |
