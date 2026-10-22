# flash

The contract of the capability `flash`: 20 blocks of durable memory of 4096 bytes each, numbered 0 to 19. Where the blocks lie on the chip is in the board reference; a caller does not need it.

## Operations

| Operation | Behaviour | Returns within |
|---|---|---|
| Read | Any range inside one block | 1 ms |
| Write | Whole 4-byte words at an offset that is a multiple of 4, inside one block. A write only changes bits from 1 to 0: afterwards a word holds the old value AND the written value. | 1 ms per word |
| Erase | One whole block. Afterwards every byte is `0xFF`. | 100 ms |

The provider fits a write or an erase between radio events. The times include that wait.

## Guarantees

- When a call has returned with success, its effect survives power loss.
- Power loss during a write leaves the words of that write undefined and every other word unchanged.
- Power loss during an erase leaves that block undefined and every other block unchanged.
- Each block endures at least 10 000 erases.
- The provider refuses a write or an erase while the supply is below 2.1 V, and any call whose range leaves the block or whose offset or length is not a multiple of 4. A refused call changes nothing and says so.
- The provider itself never writes to these blocks.

## Examples

| Case | Expected |
|---|---|
| Write `0x0000FFFF` to an erased word | The word reads `0x0000FFFF` |
| Then write `0xFFFF0000` to the same word | The word reads `0x00000000` |
| Erase block 3 | Block 3 reads 4096 times `0xFF`; all other blocks are unchanged |
| Power is lost during a write of 5 words | These 5 words are undefined; every other word of the block is unchanged |
| Power is lost during the erase of block 3 | Block 3 is undefined; all other blocks are unchanged |
| Write of 3 bytes, or at offset 6 | Refused; nothing changes |
| Write while the supply is at 2.0 V | Refused; nothing changes |
