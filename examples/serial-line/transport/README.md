# transport

Moves payloads over the serial line, one frame each way at a time, and hands the session whole payloads. It is the only part of the program that touches the port.

## Why

Two pieces of knowledge live here, and they change for different reasons: how the port is opened, written and read with deadlines, and how a stream of bytes is cut into frames again. The second is a calculation that a test can feed byte by byte, so it is a unit of its own, `framing`, and the port is `serial`. Together they are one adapter to the outside world, and nothing above them sees a byte.
