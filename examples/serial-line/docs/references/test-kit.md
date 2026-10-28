# Test kit

How every test of this project builds fakes, wires units and waits. At most 25 lines; every step reads it.

- A fake of a need is a class in `tests/fakes/<contract>.py`, one per contract, built as the contract's `## Fake` says. A test constructs it and passes it to the unit under test.
- `FakeUart`: `sent()` returns every byte written; `deliver(bytes, after_ms=0)` queues bytes; `fail_next_write()` and `fail_next_read()` arm one `failed`.
- `FakeClock`: `advance(ms)` moves `now()`; nothing else moves it. A `read` with a timeout on `FakeUart` advances the `FakeClock` it was given.
- `FakeTransport`: `sent()` returns the payloads given to `send`; `script(payload)` queues an answer for `receive`; `fail_next_send()`, `fail_next_receive()` arm `line-error`.
- The real `codec` and the real `framing` stand in for their contracts, as the contracts say.
- Unit tests live under `tests/<unit path>/`, one file per part, one test per Examples row named `test_<part>_<case>`.
- Integration tests live in `tests/integration/`, one file per scenario group, one test per scenario named `test_<scenario>`.
- `harness.py` in `tests/integration/` starts the wired system with `FakeUart` and `FakeClock` at the root needs and stops it, leaving nothing running: `with wired_system() as (host, uart, clock)`.
- `DeviceClient` in the harness speaks the protocol from proto §4 and §5 on the fake line: `expect_frame(payload)`, `answer(payload)`.
- `wait_until(predicate, timeout_ms)` polls with the fake clock; `assert_silence(uart, ms)` waits longer than the longest internal wait.
