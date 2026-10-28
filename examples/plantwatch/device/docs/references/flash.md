# flash

Contract of `hal.flash`: 20 blocks of durable memory of 4096 bytes each, numbered 0 to 19. Where the blocks lie on the chip is in the board reference of the provider; a caller does not need it. The provider itself never writes to these blocks, and it fits a write or an erase between radio events; the times below include that wait. Notation: wit.
Sources: the board of the sensor stick as `hal` abstracts it; the product parameters of plantwatch for the capacity.

## Parts

### read

Kind: query

```wit
read: func(block: u8, offset: u16, length: u16) -> result<list<u8>, flash-error>;
```

Pre: `block` is 0 to 19; the range from `offset` over `length` bytes lies inside the block.
Result: the bytes of the range, within 1 ms. A read changes nothing.
Errors: `refused` when the block does not exist or the range leaves the block; nothing changes.
Examples:

| Case | Input | Expected |
|---|---|---|
| a word after two writes | `read(3, 0, 4)` after the two writes of the examples of `write` | `00 00 00 00` |
| an erased block | `read(3, 0, 4096)` after `erase(3)` | 4096 times `FF` |
| range leaves the block | `read(3, 4094, 4)` | `refused` |

### write

Kind: command

```wit
write: func(block: u8, offset: u16, words: list<u8>) -> result<_, flash-error>;
```

Pre: `offset` and the length of `words` are multiples of 4; the range lies inside the block; the supply is at least 2.1 V.
Result: each word holds the old value AND the written value, because a write only changes bits from 1 to 0. When the call has returned with success, its effect survives power loss. Returns within 1 ms per word.
Errors: `refused` when the supply is below 2.1 V, the range leaves the block, or the offset or the length is not a multiple of 4; a refused call changes nothing and says so. Power loss during a write leaves the words of that write undefined and every other word unchanged.
Examples:

| Case | Input | Expected |
|---|---|---|
| erased word | `write(3, 0, 0x0000FFFF)` on an erased word | the word reads `0x0000FFFF` |
| second write to the same word | then `write(3, 0, 0xFFFF0000)` | the word reads `0x00000000` |
| power lost during a write of 5 words | power loss while the call runs | these 5 words are undefined; every other word of the block is unchanged |
| 3 bytes, or offset 6 | `write(3, 0, 3 bytes)` or `write(3, 6, 4 bytes)` | `refused`; nothing changes |
| weak cell | `write(3, 0, 4 bytes)` while the supply is at 2.0 V | `refused`; nothing changes |

### erase

Kind: command

```wit
erase: func(block: u8) -> result<_, flash-error>;
```

Pre: `block` is 0 to 19; the supply is at least 2.1 V.
Result: every byte of the block is `0xFF`. When the call has returned with success, its effect survives power loss. Returns within 100 ms. Each block endures at least 10 000 erases.
Errors: `refused` when the supply is below 2.1 V or the block does not exist; nothing changes. Power loss during an erase leaves that block undefined and every other block unchanged.
Examples:

| Case | Input | Expected |
|---|---|---|
| erase one block | `erase(3)` | block 3 reads 4096 times `0xFF`; all other blocks are unchanged |
| power lost during the erase | power loss while `erase(3)` runs | block 3 is undefined; all other blocks are unchanged |
| weak cell | `erase(3)` while the supply is at 2.0 V | `refused`; nothing changes |

### flash-error

Kind: type

```wit
variant flash-error { refused }
```

## Fake

20 blocks in memory with the AND rule for a write and `0xFF` after an erase. Helpers: `power-loss-during-next(call)` leaves the words or the block of the next write or erase undefined. Faults it can inject: `refused` on the next write or erase, as a weak cell would cause.
