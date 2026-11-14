# clock

Contract of the need `clock` of `serial-line`: the current time, a service of the host platform. Notation: wit.
Sources: none; the protocol says only how long a wait may take
Binding: platform
Version: 1

## Use

A consumer reads the time whenever it needs it, to measure how long it has waited. The clock has no state: `now` may be called at any time.

## Parts

### now

Kind: operation

```wit
now: func() -> u64;
```

Pre: none.
Result: milliseconds since an arbitrary start. Two calls never return a smaller value after a larger one.
Errors: none.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| monotonic | the call before returned `1000` | `now()` | `1000` or a larger value |

## Fake

A clock that stands still until a test moves it: `advance(ms)` adds to what `now` returns. Faults it can inject: none.
