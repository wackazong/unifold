# status

Kind: operation

```text
read or notify Status (0003), 17 bytes:
  offset 0  size 2  boot_counter         current tick count, first part
  offset 2  size 4  seconds_since_boot   current tick count, second part
  offset 6  size 4  oldest               sequence number of the oldest stored reading, 0 if `count` is 0
  offset 10 size 4  newest               sequence number of the newest reading ever taken, 0 if none
  offset 14 size 2  count                number of stored readings
  offset 16 size 1  flags                bit 0 `overflow`, bit 1 `bonding-open`, bit 2 `fetch-active`, bits 3 to 7 reserved
```

Pre: a connection; no encryption is required.
Result: the state of the sensor stick at the moment it sends the value. "Stored" is used as the [glossary](../glossary.md) defines it. `overflow` is 1 when the sensor stick has discarded at least one stored reading to make room, since the last successful confirm or since its start; it discards the oldest stored readings first, and the central then expects a gap in the sequence numbers. A sensor stick notifies Status after it has taken a reading and after it has carried out a confirm. A central that fetches takes its [time reference](time-reference.md) from this value.
Errors: none; Status is readable by anyone in range.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| 96 stored readings | tick count 12 / 87 305, the 96 stored readings 4711 to 4806, no flag set | read Status | `0C 00 09 55 01 00 67 12 00 00 C6 12 00 00 60 00 00` |
| After an overflow | stored readings were overwritten since the last confirm | read Status | bit 0 of `flags` is 1, until the next successful confirm or restart |
