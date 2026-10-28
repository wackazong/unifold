# reading-log

Contract of `store.reading-log`: the stored readings of the sensor stick and the mark that releases them. "Stored" means: received by the provider, and neither marked as delivered nor discarded. A reading that was accepted survives power loss and restart. At least 2 880 readings are kept; when there is no room, the oldest readings are discarded, up to 204 at once, and the summary says so. A reading is never refused for lack of room. Notation: wit.
Sources: the product parameters of plantwatch and decision 0010 of plantwatch.

## Parts

### summary

Kind: query

```wit
summary: func() -> log-summary;
```

Pre: none.
Result: the number of stored readings, the sequence numbers of the oldest and the newest stored reading, the highest sequence number ever received, the capacity, and whether stored readings were discarded since the last mark or since start. A number that does not exist is 0.
Errors: none.
Examples:

| Case | Input | Expected |
|---|---|---|
| 96 stored | `summary()` | stored 96, oldest 3145729, newest 3145824, capacity 3468 |
| after a mark up to 3145824 | `summary()` | stored 0, oldest 0, newest 0, highest received 3145824 |

### read

Kind: query

```wit
read: func(from: u32) -> result<option<reading>, log-error>;
```

Pre: none.
Result: the stored reading with the lowest sequence number at or above `from`, bit for bit as it was accepted, or none. Asked again with the number after the one returned, it yields the stored readings in ascending order. A read changes nothing and returns within 5 ms. The reading is the [reading](readings.md#reading) of `sampling`.
Errors: `failed` when the memory could not be read; nothing has changed.
Examples:

| Case | Input | Expected |
|---|---|---|
| from the start | `read(0)` with 3145729 to 3145824 stored | reading 3145729 |
| the next one | `read(3145730)` | reading 3145730, and so on up to 3145824 |
| past the newest | `read(3145825)` | none |

### mark-delivered

Kind: command

```wit
mark-delivered: func(up-to: u32) -> result<_, log-error>;
```

Pre: `up-to` is at most the highest sequence number received.
Result: every reading up to that number is no longer stored. The mark is durable when the call returns, which takes at most 200 ms. A mark at or below an earlier mark succeeds and changes nothing. Only a mark and a full memory remove a reading.
Errors: `out-of-range` when `up-to` is above the highest sequence number received; `failed` when the memory could not be written. A failed mark has changed nothing.
Examples:

| Case | Input | Expected |
|---|---|---|
| everything | `mark-delivered(3145824)` | ok; the summary shows stored 0 |
| again | `mark-delivered(3145824)` once more | ok; nothing changes |
| above the newest | `mark-delivered(3145825)` | `out-of-range` |

### log-summary

Kind: type

```wit
record log-summary {
  stored: u16,
  oldest: u32,
  newest: u32,
  highest-received: u32,
  capacity: u16,
  discarded: bool,
}
```

### log-error

Kind: type

```wit
variant log-error { out-of-range, failed }
```

## Fake

A log in memory with the same rules, whose capacity a test sets. Faults it can inject: `failed` on the next read or mark; a full memory, which discards the oldest 204 readings and sets `discarded`.
