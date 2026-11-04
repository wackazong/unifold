# flash

Contract of `hal.flash`: 20 blocks of durable memory of 4096 bytes each, numbered 0 to 19. Where the blocks lie on the chip is in the board reference of the provider; a caller does not need it. The provider itself never writes to these blocks, and it fits a write or an erase between radio events; the times in `## Qualities` include that wait. Notation: wit.
Sources: the board of the sensor stick as `hal` abstracts it; the product parameters of plantwatch for the capacity.
Binding: in-process

## Use

A write only changes bits from 1 to 0, so a caller that writes a word again erases its block first. A write and an erase need a supply of at least 2.1 V. The connection has no state beyond the content of the blocks: any part may be called at any time.

## Qualities

| Aspect | Guarantee |
|---|---|
| latency | a read returns within 1 ms, a write within 1 ms per word, an erase within 100 ms |
| durability | the effect of a write or an erase survives power loss once the call has returned with success |
| endurance | each block endures at least 10 000 erases |
| wear | the caller erases each block at most once in 12 days |
| supply | a write or an erase is refused below 2.1 V and changes nothing |
| concurrency | `hal` delivers the events and alarms of all four contracts one after another, never two at the same time; whenever no event is being handled, the board sleeps, keeps counting time and keeps the radio schedule, and draws the sleep current of the board reference |

## Parts

### read

Kind: query

```wit
read: func(block: u8, offset: u16, length: u16) -> result<list<u8>, flash-error>;
```

Pre: `block` is 0 to 19; the range from `offset` over `length` bytes lies inside the block.
Result: the bytes of the range. A read changes nothing.
Errors: `refused` when the block does not exist or the range leaves the block; nothing changes.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| a word after two writes | the two writes of the examples of `write` | `read(3, 0, 4)` | `00 00 00 00` |
| an erased block | `erase(3)` has returned | `read(3, 0, 4096)` | 4096 times `FF` |
| range leaves the block | | `read(3, 4094, 4)` | `refused` |

### write

Kind: command

```wit
write: func(block: u8, offset: u16, words: list<u8>) -> result<_, flash-error>;
```

Pre: `offset` and the length of `words` are multiples of 4; the range lies inside the block; the supply is at least 2.1 V.
Result: each word holds the old value AND the written value, because a write only changes bits from 1 to 0.
Errors: `refused` when the supply is below 2.1 V, the range leaves the block, or the offset or the length is not a multiple of 4; a refused call changes nothing and says so. Power loss during a write leaves the words of that write undefined and every other word unchanged.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| erased word | the word at block 3, offset 0 is erased | `write(3, 0, 0x0000FFFF)` | ok; the word reads `0x0000FFFF` |
| second write to the same word | the write of `erased word` | `write(3, 0, 0xFFFF0000)` | ok; the word reads `0x00000000` |
| power lost during a write of 5 words | power is lost while the call runs | `write(3, 0, 5 words)` | these 5 words are undefined; every other word of the block is unchanged |
| 3 bytes | | `write(3, 0, 3 bytes)` | `refused`; nothing changes |
| offset 6 | | `write(3, 6, 4 bytes)` | `refused`; nothing changes |
| weak cell | the supply is at 2.0 V | `write(3, 0, 4 bytes)` | `refused`; nothing changes |

### erase

Kind: command

```wit
erase: func(block: u8) -> result<_, flash-error>;
```

Pre: `block` is 0 to 19; the supply is at least 2.1 V.
Result: every byte of the block is `0xFF`.
Errors: `refused` when the supply is below 2.1 V or the block does not exist; nothing changes. Power loss during an erase leaves that block undefined and every other block unchanged.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| erase one block | | `erase(3)` | ok; block 3 reads 4096 times `0xFF`; all other blocks are unchanged |
| power lost during the erase | power is lost while the call runs | `erase(3)` | block 3 is undefined; all other blocks are unchanged |
| weak cell | the supply is at 2.0 V | `erase(3)` | `refused`; nothing changes |

### flash-error

Kind: type

```wit
variant flash-error { refused }
```

## Fake

20 blocks in memory with the AND rule for a write and `0xFF` after an erase. Helpers: `power-loss-during-next(call)` leaves the words or the block of the next write or erase undefined. Faults it can inject: `refused` on the next write or erase, as a weak cell would cause.
