# Context of session

What this unit takes over from the units above. The only file of the unit that links upward.

## From serial-line

### [serial-line/0002 Calls are synchronous, and one host instance runs one session](../../../docs/decisions/0002-calls-are-synchronous-and-one-session-per-host-instance.md)
<!-- unifold:cites sha=7a66fedd -->

Says: every call blocks until the protocol step is done; one host instance runs one session.

Here: `open` and `close` return only when the ACK arrived or the timeout passed; the state lives in the instance.

### [serial-line/0003 The host never retries an open on its own](../../../docs/decisions/0003-the-host-never-retries-an-open-on-its-own.md)
<!-- unifold:cites sha=d640df09 -->

Says: when no ACK arrives within 500 ms, open has failed and the host reports it; it does not send OPEN again.

Here: `open` returns `timeout` after one attempt and the state is closed.

### [serial-line: OPEN_TIMEOUT_MS](../../../docs/references/constants.md#open_timeout_ms)
<!-- unifold:cites sha=04423a36 -->

Says: 500 ms, from proto §5.1.

Here: the deadline of the wait for the ACK of open.
