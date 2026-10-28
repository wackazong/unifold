---
status: derived
date: 2026-10-27
derived-from: proto §4.3
---

# Bytes before a magic byte are dropped

## Source says

Proto §4.3: a receiver reads the line as a stream of bytes and discards every byte until it sees a magic byte, then reads the length, the payload and the CRC. A payload byte that equals the magic byte is part of the payload, because the length says how many bytes follow. A frame with a wrong CRC is invalid; the device drops it and waits for the next magic byte.

## Context and Problem Statement

The unit needs a rule for garbage, for a frame cut in two, and for a frame with a wrong CRC.

## Decision Outcome

Chosen option: "as §4.3 says, and keep at most `MAX_BUFFER_BYTES`", because the source settles the dropping; the buffer limit is the one addition, so that a line that never sends a magic byte cannot grow the buffer without bound.

### Consequences

- Good: the host and the device agree on what a frame is after garbage.
- Bad: a frame longer than the buffer limit can never be received; none is, since `MAX_PAYLOAD` is 255.
