# Reading log

The contract of the connection `reading-log`: the stored readings of the sensor stick, as `store` keeps them and `link` serves them. "Stored" means: received by `store`, and neither marked as delivered nor discarded.

## Operations

| Operation | Effect |
|---|---|
| Summary | The number of stored readings, the sequence numbers of the oldest and the newest stored reading, the highest sequence number ever received, the capacity, and whether stored readings were discarded since the last mark or since start. A number that does not exist is 0. |
| Read | Takes a sequence number and returns the stored reading with the lowest sequence number at or above it, or "none". Asked again with the number after the one returned, it yields the stored readings in ascending order. |
| Mark as delivered | Takes a sequence number. Every reading up to that number is no longer stored. |

## Guarantees

- A reading that was accepted survives power loss and restart and comes back from Read bit for bit.
- At least 2 880 readings are kept. When there is no room, the oldest readings are discarded, up to 204 at once, and the summary says so. A reading is never refused for lack of room.
- Read changes nothing. Only a mark and a full memory remove a reading.
- A mark is durable when the call returns. A mark at or below an earlier mark succeeds and changes nothing. A mark above the highest sequence number received is refused.
- A failed read or mark is reported and has changed nothing.
- Read returns within 5 ms, a mark within 200 ms.

## Example

```text
summary             -> stored 96, oldest 3145729, newest 3145824, capacity 3468
read 0              -> 3145729
read 3145730        -> 3145730        ... and so on up to 3145824
read 3145825        -> none
mark up to 3145824  -> ok
summary             -> stored 0, oldest 0, newest 0, highest received 3145824
```
