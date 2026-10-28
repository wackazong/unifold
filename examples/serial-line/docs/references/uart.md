# uart

Contract of the need `uart` of `serial-line`: the serial port of the host computer, opened at 115200 baud, 8 data bits, no parity, one stop bit. Notation: wit.
Sources: proto §3

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

| Case | Input | Expected |
|---|---|---|
| a frame | `write([1F, 01, 01, 12])` | ok, the port received the four bytes |
| port gone | `write([1F])` after the port failed | `failed` |

### read

Kind: query

```wit
read: func(max: u16, timeout-ms: u32) -> result<list<u8>, uart-error>;
```

Pre: the port is open.
Result: the bytes that arrived, at most `max`, as soon as at least one arrived or `timeout-ms` passed. An empty list means that nothing arrived in time.
Errors: `failed` when the port reported an error.
Examples:

| Case | Input | Expected |
|---|---|---|
| bytes waiting | `read(64, 50)` with `1F 01 81 9B` waiting | `[1F, 01, 81, 9B]` |
| silence | `read(64, 50)`, nothing arrives | `[]` after 50 ms |
| port gone | `read(64, 50)` after the port failed | `failed` |

### uart-error

Kind: type

```wit
variant uart-error { failed }
```

## Fake

A port in memory: `write` records the bytes, `read` delivers bytes that the test has scripted, in the order and with the delays the test set, and answers empty when nothing is scripted for the time. Helpers: `sent()` returns every byte written so far; `deliver(bytes)` queues bytes for the next reads; `fail-next-write()` and `fail-next-read()` arm `failed` once.
