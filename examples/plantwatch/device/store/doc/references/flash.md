# flash as store expects it

The contract of the need `flash`: the durable memory `store` requires of
whoever provides it. The [flash layout](flash-layout.md) is built on these
properties and on nothing else.

| Property | What `store` expects |
|---|---|
| Size | At least 20 blocks of 4096 bytes, addressed by block number and offset |
| Read | Any range inside a block, within 1 ms |
| Write | Whole 4-byte words. A write can only turn bits from 1 to 0. Within 1 ms per word. |
| Erase | A whole block. Afterwards every byte is `0xFF`. Within 100 ms. |
| Endurance | At least 10 000 erases per block |
| Durability | When a write or an erase has returned, its effect survives power loss |
| Power loss during a write | Only the words of that write are undefined |
| Power loss during an erase | Only that block is undefined |
| Refusal | A write or an erase may be refused, for example when the cell is weak. Then no bit has changed, and `store` is told. |
| Exclusive use | Nobody else writes to these blocks |

## How store uses it

`store` writes 5 words per reading and 2 words per mark, always to erased
memory. It erases a ring block once per 3 672 readings, at the shortest
sampling interval about once in 12 days, and a journal block once per
1 020 marks.

## Examples

The cases a provider has to pass, a substitute included.

| Case | Expected |
|---|---|
| 20 bytes are written to erased memory and read back | The same 20 bytes, also after power loss that follows the return |
| Power is cut after the third of 5 words of a write | These 5 words may hold anything. Every other byte of the 20 blocks is as before. |
| A ring block is erased | Its 4096 bytes are `0xFF`. The journal blocks are as before. |
| Power is cut during that erase | That block may hold anything. The other 19 are as before. |
| A write is refused | No bit of any block has changed |
