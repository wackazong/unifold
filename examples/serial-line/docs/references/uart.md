# uart

Contract of the need `uart` of `serial-line`: the serial port of the host computer, opened at 115200 baud, 8 data bits, no parity, one stop bit. Notation: wit.
Sources: proto §3
Binding: serial
Version: 1

## Use

The consumer writes bytes to the port and reads the bytes that arrived. The port is open for the whole run of the program, so the connection has no state of its own: `write` and `read` may be called at any time.

## Qualities

| Aspect | Guarantee |
|---|---|
| concurrency | one caller at a time |
| ordering | bytes are handed to the port, and delivered from it, in the order in which they were written or arrived |
| timeout | `read` returns as soon as at least one byte arrived, or empty once `timeout-ms` have passed |

## Parts

### write

Kind: command

```wit
write: func(bytes: list<u8>) -> result<_, uart-error>;
```

Pre: the port is open.
Result: every byte was handed to the port, in order.
Errors: `failed` when the port reported an error; the bytes may be partly written.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| a frame | the port is open | `write([1F, 01, 01, 12])` | ok |
| port gone | the port failed | `write([1F])` | `failed` |

### read

Kind: query

```wit
read: func(max: u16, timeout-ms: u32) -> result<list<u8>, uart-error>;
```

Pre: the port is open.
Result: the bytes that arrived, at most `max`, as soon as at least one arrived or `timeout-ms` passed. An empty list means that nothing arrived in time.
Errors: `failed` when the port reported an error.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| bytes waiting | `1F 01 81 9B` are waiting | `read(64, 50)` | `[1F, 01, 81, 9B]` |
| silence | nothing arrives for 50 ms | `read(64, 50)` | `[]` |
| port gone | the port failed | `read(64, 50)` | `failed` |

### uart-error

Kind: type

```wit
variant uart-error { failed }
```

## Fake

A port in memory: `write` records the bytes, `read` delivers bytes that the test has scripted, in the order and with the delays the test set, and answers empty when nothing is scripted for the time. Helpers: `sent()` returns every byte written so far; `deliver(bytes)` queues bytes for the next reads; `fail-next-write()` and `fail-next-read()` arm `failed` once.
