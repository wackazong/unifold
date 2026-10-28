# frames

Contract of `codec.frames`, the layout of a frame. Notation: wit.
Sources: proto §4

## Parts

### encode

Kind: query

```wit
encode: func(payload: list<u8>) -> result<list<u8>, encode-error>;
```

Pre: `len(payload) <= MAX_PAYLOAD`.
Result: the bytes of one frame: `MAGIC_BYTE`, the length, the payload, then the CRC-8 over length and payload with `CRC_POLY` and `CRC_INIT`.
Errors: `too-long` when the payload exceeds `MAX_PAYLOAD`.
Examples:

| Case | Input | Expected |
|---|---|---|
| empty payload, proto §4.2 | `encode([])` | `1F 00 00` |
| OPEN, proto §4.2 | `encode([01])` | `1F 01 01 12` |
| DATA hi, proto §4.2 | `encode([03, 68, 69])` | `1F 03 03 68 69 C2` |
| longest payload | 255 bytes `00` | 258 bytes, the last `D7` |
| one over the limit | 256 bytes | `too-long` |

### decode

Kind: query

```wit
decode: func(bytes: list<u8>) -> result<decoded, decode-error>;
```

Pre: none.
Result: the frame at the start of `bytes` and how many bytes it used. Bytes after the frame are not read.
Errors: `bad-magic` when the first byte is not `MAGIC_BYTE`; `incomplete` when the bytes end before the frame does; `bad-crc` when the CRC does not match.
Examples:

| Case | Input | Expected |
|---|---|---|
| ACK, proto §4.2 | `decode([1F, 01, 81, 9B])` | payload `[81]`, used 4 |
| trailing bytes | `decode([1F, 00, 00, 1F])` | payload `[]`, used 3 |
| garbage, proto §4.3 | `decode([00, 1F, 01, 81, 9B])` | `bad-magic` |
| cut short | `decode([1F, 01, 81])` | `incomplete` |
| wrong CRC | `decode([1F, 01, 81, 00])` | `bad-crc` |
| magic byte inside the payload, proto §4.3 | `decode([1F, 01, 1F, D5])` | `bad-crc` |

### decoded

Kind: type

```wit
record decoded { payload: list<u8>, used: u16 }
```

| Field | Meaning |
|---|---|
| payload | the payload of the frame, without magic, length and CRC |
| used | how many bytes of the input the frame took |

### encode-error

Kind: type

```wit
variant encode-error { too-long }
```

### decode-error

Kind: type

```wit
variant decode-error { bad-magic, incomplete, bad-crc }
```

## Fake

The real implementation: the codec is small, deterministic and has no side effects, and its users produce inputs that no examples table can list.
