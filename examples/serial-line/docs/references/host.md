# host

Contract of `serial-line.host`, the calls a program makes to run a session. Notation: wit.
Sources: proto §5
Binding: in-process
Version: 1

## Use

A host program opens a session, sends data while it is open, and closes it. A failed line closes the session. After `open` fails with `timeout`, the device has not answered and the session is still closed; the program decides whether to call `open` again, the host never retries on its own. After `send` fails with `line-error`, the session is closed and every further `send` fails with `not-open`; the program calls `open` before it sends again.

## States

Start: closed.

| State | Part | Result | Next |
|---|---|---|---|
| closed | `open` | ok | open |
| closed | `send` | `not-open` | closed |
| closed | `close` | `not-open` | closed |
| open | `open` | `already-open` | open |
| open | `send` | ok | open |
| open | `send` | `line-error` | closed |
| open | `close` | | closed |

## Qualities

| Aspect | Guarantee |
|---|---|
| concurrency | one call at a time: the program waits for each call to return before it makes the next |
| timeout | `open` waits for the ACK at most `OPEN_TIMEOUT_MS`, `close` at most `CLOSE_TIMEOUT_MS`; `send` awaits nothing |

## Parts

### open

Kind: operation

```wit
open: func() -> result<_, session-error>;
```

Pre: none.
Result: `OP_OPEN` was sent as one frame, the ACK arrived within `OPEN_TIMEOUT_MS`, and the state is open.
Errors: `already-open` when the state is not closed, the state is unchanged; `timeout` when no ACK arrived within `OPEN_TIMEOUT_MS`, the state is closed again; `line-error` when the line failed, the state is closed.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| device answers, proto §5.1 | the line answers `1F 01 81 9B` | `open()` | ok |
| device silent, proto §5.1 | nothing arrives for `OPEN_TIMEOUT_MS` | `open()` | `timeout` |
| opened twice, proto §5.4 | the state is open | `open()` | `already-open` |

### send

Kind: operation

```wit
send: func(data: list<u8>) -> result<_, session-error>;
```

Pre: `len(data) <= MAX_DATA`.
Result: one frame with the payload `OP_DATA` followed by `data` was sent: `1F 03 03 68 69 C2` for the data `68 69`. Nothing is awaited.
Errors: `not-open` when the state is not open, nothing is sent; `too-long` when the data has more than `MAX_DATA` bytes, nothing is sent; `line-error` when the write failed.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| two bytes, proto §4.2 | the state is open | `send([68, 69])` | ok |
| longest data | the state is open | `send(254 bytes 00)` | ok |
| one over the limit | the state is open | `send(255 bytes 00)` | `too-long` |
| closed | the state is closed | `send([68])` | `not-open` |

### close

Kind: operation

```wit
close: func() -> result<_, session-error>;
```

Pre: none.
Result: `OP_CLOSE` was sent, and the state is closed, whether the ACK arrived or `CLOSE_TIMEOUT_MS` passed.
Errors: `not-open` when the state is not open; `line-error` when the line failed, the state is closed.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| device answers, proto §5.2 | the line answers `1F 01 82 92` | `close()` | ok |
| device silent, proto §5.2 | nothing arrives for `CLOSE_TIMEOUT_MS` | `close()` | ok |

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

Replays the examples: answers the calls of the examples table with their results and fails any other call with `unexpected-call`. Faults it can inject: none. Shipped with the library for the tests of host programs; this project's own integration tests do not use it, the harness drives the real session through a test client on the line.
