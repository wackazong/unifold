# host

Contract of `serial-line.host`, the calls a program makes to run a session. Notation: wit.
Sources: proto §5

## Parts

### open

Kind: command

```wit
open: func() -> result<_, session-error>;
```

Pre: the state is closed.
Result: `OP_OPEN` was sent as one frame, the ACK arrived within `OPEN_TIMEOUT_MS`, and the state is open.
Errors: `already-open` when the state is not closed; `timeout` when no ACK arrived within `OPEN_TIMEOUT_MS`, the state is closed again; `line-error` when the line failed, the state is closed.
Examples:

| Case | Input | Expected |
|---|---|---|
| device answers, proto §5.1 | `open()`, the line answers `1F 01 81 9B` | ok, state open |
| device silent, proto §5.1 | `open()`, nothing arrives for `OPEN_TIMEOUT_MS` | `timeout`, state closed |
| opened twice, proto §5.4 | `open()` while open | `already-open`, state unchanged |

### send

Kind: command

```wit
send: func(data: list<u8>) -> result<_, session-error>;
```

Pre: the state is open; `len(data) <= MAX_DATA`.
Result: one frame with the payload `OP_DATA` followed by `data` was sent. Nothing is awaited.
Errors: `not-open` when the state is not open; `too-long` when `data` has more than `MAX_DATA` bytes; `line-error` when the write failed.
Examples:

| Case | Input | Expected |
|---|---|---|
| two bytes, proto §4.2 | `send([68, 69])` while open | ok, the line carries `1F 03 03 68 69 C2` |
| longest data | 254 bytes | ok |
| one over the limit | 255 bytes | `too-long`, nothing sent |
| closed | `send([68])` while closed | `not-open`, nothing sent |

### close

Kind: command

```wit
close: func() -> result<_, session-error>;
```

Pre: the state is open.
Result: `OP_CLOSE` was sent, and the state is closed, whether the ACK arrived or `CLOSE_TIMEOUT_MS` passed.
Errors: `not-open` when the state is not open; `line-error` when the line failed, the state is closed.
Examples:

| Case | Input | Expected |
|---|---|---|
| device answers, proto §5.2 | `close()`, the line answers `1F 01 82 92` | ok, state closed |
| device silent, proto §5.2 | `close()`, nothing arrives for `CLOSE_TIMEOUT_MS` | ok, state closed |

### session-error

Kind: type

```wit
variant session-error { already-open, not-open, too-long, timeout, line-error }
```

| Case | Meaning |
|---|---|
| already-open | open was called while the state is not closed |
| not-open | send or close was called while the state is not open |
| too-long | the data does not fit into one frame |
| timeout | the device did not answer within the time the protocol allows |
| line-error | the serial line failed; the session is closed |

## Fake

Replays the examples. Any other call fails with `unexpected-call`. Faults it can inject: none; the integration harness drives the real session through a test client on the line.
