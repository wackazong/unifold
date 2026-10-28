# session

The host side of a session: it opens, sends data and closes, and it knows at every moment which of the four states of the protocol it is in. Programs call it; it is the only unit that talks to callers.

## Why

The protocol's state table is the one thing a caller can get wrong, so it lives in one unit that refuses an open while open and a send while closed. Timeouts are measured with a clock the unit is given, never with sleeps, so a test of the 500 ms rule takes no time. The unit knows nothing about bytes: it sends payloads and gets payloads back, and whatever moves them is behind the need `transport`.
