# Flash layout

How store arranges readings and delivered marks in the blocks it gets
through `flash`. Layout version 1. Nothing outside store reads these
blocks.

## Blocks

| Blocks | Role | Content |
|---|---|---|
| 0 to 17 | Ring | Readings, in the order in which they were received |
| 18 and 19 | Journal | Delivered marks |

Every block in use starts with a header of 16 bytes. All multi-byte
numbers are little-endian. An erased byte is `0xFF`.

### Block header

| Offset | Size | Field | Content |
|---|---|---|---|
| 0 | 4 | `magic` | `0x474C5750`, the bytes `PWLG` |
| 4 | 1 | `layout` | Layout version: 1 |
| 5 | 1 | `role` | `0x01` ring, `0x02` journal |
| 6 | 2 | | `0x0000` |
| 8 | 4 | `serial` | Rises by one with every block that store starts in this role |
| 12 | 4 | `check` | CRC-32 of bytes 0 to 11 |

A block whose header is erased is empty. A block whose header is neither
erased nor valid is treated as empty and erased before use.

## Ring

A ring block holds 204 slots of 20 bytes after the header. store fills the
slots of a block in ascending order and the blocks in ascending order of
block number, from 17 back to 0.

### Slot

| Offset | Size | Field | Content |
|---|---|---|---|
| 0 | 1 | `marker` | `0xA5` |
| 1 | 1 | `present` | Bit 0 soil moisture, bit 1 light, bit 2 temperature. 1: present. |
| 2 | 2 | `boot_counter` | Unsigned |
| 4 | 4 | `sequence_number` | Unsigned |
| 8 | 4 | `seconds_since_boot` | Unsigned |
| 12 | 2 | `soil_moisture` | Unsigned, percent × 10 |
| 14 | 2 | `temperature` | Signed, °C × 10 |
| 16 | 3 | `light` | Unsigned, lux |
| 19 | 1 | `check` | CRC-8 (polynomial `0x07`, start value `0x00`) of bytes 0 to 18 |

The bytes of an absent quantity are `0x00`.

| State of a slot | How store recognises it | Treatment |
|---|---|---|
| Free | All 20 bytes are `0xFF` | Next reading goes here |
| Reading | `marker` is `0xA5` and `check` is right | A reading of the log |
| Void | Anything else | Skipped. Left by a write that power loss interrupted. |

store writes a slot once and never writes to it again.

### Starting a new block

When the last slot of the newest block is used, the next reading needs the
following block.

1. If that block is not empty, store erases it. It is the block with the
   lowest `serial`. Stored readings in it are discarded; store sets the
   "discarded" flag of its summary if any of them was not yet delivered.
2. store writes the header with `serial` one higher than that of the
   newest block.
3. store writes the reading into the first slot.

## Journal

A journal block holds 510 entries of 8 bytes after the header.

| Offset | Size | Field | Content |
|---|---|---|---|
| 0 | 4 | `delivered_up_to` | Sequence number of a mark |
| 4 | 4 | `inverse` | Every bit of `delivered_up_to` inverted |

- A mark is the next free entry of the journal block with the higher
  `serial`.
- An entry whose two fields do not match is skipped.
- The valid mark is the highest `delivered_up_to` of all valid entries.
- When the block is full, store erases the other journal block, writes its
  header with the next `serial`, and writes the mark as its first entry.
  The full block keeps the previous mark until then.
- store writes no entry for a mark that is not higher than the valid mark.

## What is stored

A reading of the ring is stored if its sequence number is higher than the
valid mark. Because a mark covers only readings that were received before
it, discarding an old ring block never brings a delivered reading back.

## Recovery at start

1. Read the 20 headers. Erase a block whose header is invalid.
2. The ring block with the highest `serial` is the newest. Its first free
   slot is where the next reading goes. If no ring block has a header,
   the ring is empty and starts at block 0.
3. The valid mark is taken from both journal blocks.
4. Count the readings above the valid mark, and note the lowest and the
   highest sequence number among them.

Recovery reads at most 80 kB and writes nothing unless a block is invalid.

## Numbers

| Quantity | Value |
|---|---|
| Slots per ring block | (4096 − 16) / 20 = 204 |
| Slots in 18 ring blocks | 3 672 |
| Readings held in the worst case, one block just erased | 17 × 204 = 3 468 |
| Erases of one ring block | One per 3 672 readings: every 38 days at 96 readings a day |
| Entries per journal block | (4096 − 16) / 8 = 510 |
| Erases of one journal block | One per 1 020 marks |
