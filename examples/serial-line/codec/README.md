# codec

Turns a payload into the bytes of one frame and the bytes of one frame back into a payload. A pure calculation: no port, no buffer, no time.

## Why

This unit hides the frame layout and its checksum, which [decision 0001](docs/decisions/0001-a-frame-is-magic-length-payload-and-crc.md) takes from the protocol. The layout is the one thing both directions of the line must agree on, so it is written once and tested against the vectors of the protocol. Because the unit is pure, its users take the real thing in their tests instead of a fake, which could only disagree with it. It does not know where a frame starts in a stream of bytes; that is a policy of the line, not of the layout.
