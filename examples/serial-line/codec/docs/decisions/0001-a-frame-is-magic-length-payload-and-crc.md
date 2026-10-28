---
status: derived
date: 2026-10-27
derived-from: proto §4.1, Table 3
---

# A frame is magic, length, payload and CRC

## Source says

Proto §4.1, Table 3: a frame is one magic byte 0x1F, one length byte with the number of payload bytes from 0 to 255, the payload, and one CRC byte. The CRC is CRC-8 with the polynomial 0x07, initial value 0x00, no reflection and no final XOR, over the length byte followed by the payload. §4.2 gives six frames as examples.

## Context and Problem Statement

The layout is the secret of this unit; the source fixes every field.

## Decision Outcome

Chosen option: "Table 3 as written", because the source settles it. The examples of §4.2 are the first tests, word for word, in the contract `frames`.

### Consequences

- Good: no choice is left to the implementer.
- Bad: none.
