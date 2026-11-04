# Context of session

What this unit takes over from the units above, and what each item means here.

## From serial-line

### [serial-line/0002 Calls are synchronous, and one host instance runs one session](../../../docs/decisions/0002-calls-are-synchronous-and-one-session-per-host-instance.md)

Every call blocks until the protocol step is done; one host instance runs one session. `open` and `close` return only when the ACK arrived or the timeout passed; the state lives in the instance.

### [serial-line/0003 The host never retries an open on its own](../../../docs/decisions/0003-the-host-never-retries-an-open-on-its-own.md)

When no ACK arrives within 500 ms, open has failed and the host reports it; it does not send OPEN again. `open` returns `timeout` after one attempt and the state is closed.

### [serial-line: OPEN_TIMEOUT_MS](../../../docs/references/constants.md#open_timeout_ms)

The constant is 500 ms, from proto §5.1. It sets the deadline of the wait for the ACK of open.
