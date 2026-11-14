# reading-log

Contract of `store.reading-log`: the stored readings of the sensor stick and the mark that releases them. "Stored" means: received by the provider, and neither marked as delivered nor discarded. Notation: wit.
Sources: the product parameters of plantwatch.
Binding: in-process

## Use

The caller reads the summary and the stored readings in ascending order, and marks the readings up to a sequence number as delivered. A mark covers every reading up to its number and may be repeated. Only a mark and a full memory remove a reading. When the memory refuses a write or an erase, a mark fails and says so, and a reading handed over is not stored; the log is then as it was before. The log draws no conclusion from gaps between sequence numbers. The connection has no state beyond the stored readings: any part may be called at any time.

## Qualities

| Aspect | Guarantee |
|---|---|
| capacity | at least 2 880 readings are kept; when there is no room, the oldest readings are discarded, up to 204 at once, and the summary says so; a reading is never refused for lack of room |
| durability | a reading that was accepted survives power loss and restart; a mark is durable when the call returns; power loss at any moment costs at most the reading or the mark that was being written, and everything written before is intact |
| availability | after a start the log is complete before the first new reading is accepted; recovery takes less than 100 ms, or less than 200 ms when power was lost during an erase |
| latency | a read returns within 5 ms, a mark within 200 ms, usually up to 2 ms and up to 110 ms once in 510 marks; accepting a reading takes up to 5 ms, and up to 110 ms once in 204 readings |

## Parts

### summary

Kind: operation

```wit
summary: func() -> log-summary;
```

Pre: none.
Result: the number of stored readings, the sequence numbers of the oldest and the newest stored reading, the highest sequence number ever received, the capacity, and whether stored readings were discarded since the last mark or since start. A number that does not exist is 0.
Errors: none.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| 96 stored | the readings 3145729 to 3145824 are stored | `summary()` | stored 96, oldest 3145729, newest 3145824, capacity 3468 |
| after a mark | `mark-delivered(3145824)` has returned | `summary()` | stored 0, oldest 0, newest 0, highest received 3145824 |

### read

Kind: operation

```wit
read: func(from: u32) -> result<option<reading>, log-error>;
```

Pre: none.
Result: the stored reading with the lowest sequence number at or above `from`, bit for bit as it was accepted, or none. Asked again with the number after the one returned, it yields the stored readings in ascending order. A read changes nothing. The reading is the [reading](readings.md#reading) of `sampling`.
Errors: `failed` when the memory could not be read; nothing has changed.
Examples: the readings 3145729 to 3145824 are stored.

| Case | Input | Expected |
|---|---|---|
| from the start | `read(0)` | reading 3145729 |
| the next one | `read(3145730)` | reading 3145730, and so on up to 3145824 |
| past the newest | `read(3145825)` | none |

### mark-delivered

Kind: operation

```wit
mark-delivered: func(up-to: u32) -> result<_, log-error>;
```

Pre: `up-to` is at most the highest sequence number received.
Result: every reading up to that number is no longer stored. A mark at or below an earlier mark succeeds and changes nothing.
Errors: `out-of-range` when `up-to` is above the highest sequence number received; `failed` when the memory could not be written. A failed mark has changed nothing.
Examples: the readings 3145729 to 3145824 are stored.

| Case | Given | Input | Expected |
|---|---|---|---|
| everything | | `mark-delivered(3145824)` | ok; the summary shows stored 0 |
| again | the mark of `everything` | `mark-delivered(3145824)` | ok; nothing changes |
| above the newest | | `mark-delivered(3145825)` | `out-of-range` |

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
