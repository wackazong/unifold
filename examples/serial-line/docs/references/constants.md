---
name-pattern: "\\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\\b"
---
# Constants

Every fixed value the code needs, under the name the code uses. Everywhere else a value is named, never written out.

| Name | Value | Unit | Source |
|---|---|---|---|
| `MAGIC_BYTE` | `0x1F` | | proto §4.1 Table 3 |
| `MAX_PAYLOAD` | 255 | bytes | proto §4.1 Table 3 |
| `MAX_DATA` | 254 | bytes | proto §5.3 |
| `CRC_POLY` | `0x07` | | proto §4.1 |
| `CRC_INIT` | `0x00` | | proto §4.1 |
| `OPEN_TIMEOUT_MS` | 500 | ms | proto §5.1 |
| `CLOSE_TIMEOUT_MS` | 500 | ms | proto §5.2 |
| `OP_OPEN` | `0x01` | | proto §5.1 |
| `OP_CLOSE` | `0x02` | | proto §5.2 |
| `OP_DATA` | `0x03` | | proto §5.3 |
| `ACK_BIT` | `0x80` | | proto §2 |
| `READ_POLL_MS` | 50 | ms | transport/0002 |
| `MAX_BUFFER_BYTES` | 1024 | bytes | transport/framing/0001 |
