# transport

Contract of `transport.transport`, moving one payload at a time over the line. Notation: wit.
Sources: proto §3, §4

## Parts

### send

Kind: command

```wit
send: func(payload: list<u8>) -> result<_, transport-error>;
```

Pre: `len(payload) <= MAX_PAYLOAD`.
Result: the payload was written to the line as exactly one frame.
Errors: `too-long` when the payload exceeds `MAX_PAYLOAD`; `line-error` when the write failed.
Examples:

| Case | Input | Expected |
|---|---|---|
| OPEN, proto §4.2 | `send([01])` | the line carries `1F 01 01 12` |
| empty payload, proto §4.2 | `send([])` | the line carries `1F 00 00` |
| one over the limit | 256 bytes | `too-long`, nothing written |
| port fails | `send([01])` while the port fails | `line-error` |

### receive

Kind: query

```wit
receive: func(deadline-ms: u32) -> result<list<u8>, transport-error>;
```

Pre: none.
Result: the payload of the next valid frame on the line, as soon as it is complete. Bytes before a magic byte are dropped. Bytes after the frame stay for the next call.
Errors: `timeout` when no complete valid frame arrived within `deadline-ms`; `line-error` when the read failed.
Examples:

| Case | Input | Expected |
|---|---|---|
| ACK arrives, proto §4.2 | the line delivers `1F 01 81 9B` | `[81]` |
| garbage first, proto §4.3 | the line delivers `00 FF 1E 1F 01 81 9B` | `[81]` |
| two frames in one read | the line delivers `1F 01 81 9B 1F 00 00` | `[81]`, then `[]` on the next call |
| silence | nothing arrives for `deadline-ms` | `timeout` |

### transport-error

Kind: type

```wit
variant transport-error { too-long, timeout, line-error }
```

## Fake

Replays the examples: `send` records the payload and answers ok, `receive` answers the next scripted payload or `timeout`. Any other call fails with `unexpected-call`. Faults it can inject: `line-error` on the next send, `line-error` on the next receive.
