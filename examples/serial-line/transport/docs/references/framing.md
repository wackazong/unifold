# framing

Contract of `framing.framing`, cutting the byte stream of the line into frames. Notation: wit.
Sources: proto §4.3

## Parts

### feed

Kind: query

```wit
feed: func(buffer: list<u8>, incoming: list<u8>) -> fed;
```

Pre: `len(buffer) + len(incoming) <= MAX_BUFFER_BYTES + MAX_PAYLOAD + 3`.
Result: every complete valid frame at the start of `buffer` followed by `incoming`, in order; `rest` holds the bytes after the last frame, starting at a magic byte or empty; bytes before a magic byte and the bytes of a frame with a wrong CRC are dropped and counted in `dropped`. When `rest` would exceed `MAX_BUFFER_BYTES`, its oldest bytes are dropped.
Errors: none.
Examples:

| Case | Input | Expected |
|---|---|---|
| one frame, proto §4.2 | `feed([], [1F, 01, 81, 9B])` | frames `[[81]]`, rest `[]`, dropped 0 |
| garbage first, proto §4.3 | `feed([], [00, FF, 1E, 1F, 01, 81, 9B])` | frames `[[81]]`, rest `[]`, dropped 3 |
| two frames | `feed([], [1F, 01, 81, 9B, 1F, 00, 00])` | frames `[[81], []]`, rest `[]`, dropped 0 |
| split frame | `feed([1F, 01], [81, 9B])` | frames `[[81]]`, rest `[]`, dropped 0 |
| incomplete | `feed([], [1F, 01, 81])` | frames `[]`, rest `[1F, 01, 81]`, dropped 0 |
| wrong CRC, proto §4.3 | `feed([], [1F, 01, 81, 00, 1F, 00, 00])` | frames `[[]]`, rest `[]`, dropped 4 |
| buffer full | `feed(1024 bytes without a magic byte, [1F])` | frames `[]`, rest `[1F]`, dropped 1024 |

### fed

Kind: type

```wit
record fed { frames: list<list<u8>>, rest: list<u8>, dropped: u32 }
```

| Field | Meaning |
|---|---|
| frames | the payloads of the complete valid frames, in order |
| rest | the bytes to keep for the next call |
| dropped | how many bytes were thrown away |

## Fake

The real implementation: a pure function over two byte lists, and its user produces every split of a stream that no table can list.
