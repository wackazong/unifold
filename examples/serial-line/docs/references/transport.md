# transport

Contract of `transport.transport`, moving one payload at a time over the line. Notation: wit.
Sources: proto §3, §4
Binding: in-process

## Use

The consumer sends a payload as one frame, and receives the payload of the next frame with a deadline. The connection has no state: `send` and `receive` may be called at any time. Bytes that arrive after a frame wait for the next `receive`.

## Qualities

| Aspect | Guarantee |
|---|---|
| concurrency | one caller at a time |
| ordering | `receive` returns the payloads in the order in which the frames arrived; a frame that arrived with the one before waits in the buffer for the next call |
| timeout | `receive` returns as soon as a complete valid frame is there, or fails with `timeout` once `deadline-ms` have passed |

## Parts

### send

Kind: operation

```wit
send: func(payload: list<u8>) -> result<_, transport-error>;
```

Pre: `len(payload) <= MAX_PAYLOAD`.
Result: the payload was written to the line as exactly one frame, laid out as [`encode`](frames.md#encode) of frames says: `send([01])` puts `1F 01 01 12` on the line, `send([])` puts `1F 00 00`.
Errors: `too-long` when the payload exceeds `MAX_PAYLOAD`, nothing is written; `line-error` when the write failed.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| OPEN, proto §4.2 | the port works | `send([01])` | ok |
| empty payload, proto §4.2 | the port works | `send([])` | ok |
| one over the limit | the port works | `send(256 bytes 00)` | `too-long` |
| port fails | the port fails | `send([01])` | `line-error` |

### receive

Kind: operation

```wit
receive: func(deadline-ms: u32) -> result<list<u8>, transport-error>;
```

Pre: none.
Result: the payload of the next valid frame on the line, as soon as it is complete. Bytes before a magic byte are dropped. Bytes after the frame stay for the next call.
Errors: `timeout` when no complete valid frame arrived before the deadline; `line-error` when the read failed.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| ACK arrives, proto §4.2 | the line delivers `1F 01 81 9B` | `receive(OPEN_TIMEOUT_MS)` | `[81]` |
| garbage first, proto §4.3 | the line delivers `00 FF 1E 1F 01 81 9B` | `receive(OPEN_TIMEOUT_MS)` | `[81]` |
| two frames in one read | the line delivers `1F 01 81 9B 1F 00 00` | `receive(OPEN_TIMEOUT_MS)` | `[81]` |
| second frame from the buffer | the call before left the frame `1F 00 00` in the buffer | `receive(OPEN_TIMEOUT_MS)` | `[]` |
| silence | nothing arrives for `OPEN_TIMEOUT_MS` | `receive(OPEN_TIMEOUT_MS)` | `timeout` |

### transport-error

Kind: type

```wit
variant transport-error { too-long, timeout, line-error }
```

## Fake

Replays the examples: `send` records the payload and answers ok, `receive` answers the next scripted payload or `timeout`. Any other call fails with `unexpected-call`. Faults it can inject: `line-error` on the next send, `line-error` on the next receive.
