# A contract written out

The contract of a connection that carries frames, written out in full as [contracts.md](contracts.md) says. The outer fence is shown as four backticks only here:

````markdown
# frames

Contract of `codec.frames`, the layout of a frame. Notation: wit.
Sources: proto §4

## Use

A consumer encodes a payload into a frame. The connection has no state: any part may be called at any time, also at the same time.

## Parts

### encode

Kind: query

```wit
encode: func(payload: list<u8>) -> result<frame, encode-error>;
```

Pre: `len(payload) <= MAX_PAYLOAD`.
Result: a frame whose first byte is `MAGIC_BYTE`, then the payload.
Errors: `too-long` when the payload exceeds `MAX_PAYLOAD`.
Examples:

| Case | Input | Expected |
|---|---|---|
| empty payload, proto §4.2 | `encode([])` | `1F 00` |
| one over the limit | 256 bytes | `too-long` |

### frame

Kind: type

```wit
record frame { magic: u8, payload: list<u8> }
```

| Field | Meaning |
|---|---|
| magic | always `MAGIC_BYTE` |

### encode-error

Kind: type

```wit
variant encode-error { too-long }
```

## Fake

Replays the examples. Any other call fails with `unexpected-call`. Faults it can inject: none.
````

The template is also in the `unifold` skill, with one for a contract folder.
