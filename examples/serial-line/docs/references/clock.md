# clock

Contract of the need `clock` of `serial-line`: the current time, a service of the host platform. Notation: wit.
Sources: none; the protocol says only how long a wait may take

## Parts

### now

Kind: query

```wit
now: func() -> u64;
```

Pre: none.
Result: milliseconds since an arbitrary start. Two calls never return a smaller value after a larger one.
Errors: none.
Examples:

| Case | Input | Expected |
|---|---|---|
| monotonic | `now()` twice | the second value is not smaller than the first |

## Fake

A clock that stands still until a test moves it: `advance(ms)` adds to what `now` returns. Faults it can inject: none.
