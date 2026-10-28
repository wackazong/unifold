# transfer-result

Kind: type

```text
indication on Transfer control: 80 <op code answered> <result code> <bytes of the answer>
  fetch:            sent: 2 bytes, last: 4 bytes, more: 1 byte     length 10
  confirm:          count: 2 bytes, oldest: 4 bytes                length 9
  abort:            none                                           length 3
  unknown op code:  none                                           length 3
```

The central writes requests to Transfer control and receives one result per request as an indication. Every result starts with `0x80`, the op code it answers and a result code. When the result code is neither `success` nor `aborted`, the bytes after it are 0. The op codes are `0x01` `fetch`, `0x02` `confirm` and `0x03` `abort`.

| Code | Name | Meaning |
|---|---|---|
| `0x00` | `success` | The request has been carried out |
| `0x01` | `op-code-not-supported` | The sensor stick does not know the op code |
| `0x02` | `invalid-parameter` | The request is shorter than its op code requires |
| `0x03` | `out-of-range` | `confirm` names a sequence number above the newest reading taken |
| `0x04` | `aborted` | The fetch ended because the central wrote `abort` |
| `0x05` | `storage-failure` | The sensor stick could not read or change its stored readings |
| `0x06` | `mtu-too-small` | A record does not fit into one notification with the current ATT MTU |

The sensor stick rejects the write itself in these cases, and no indication follows:

| ATT error | When |
|---|---|
| `0xFD` CCC descriptor improperly configured | Indications of Transfer control are not enabled, or `fetch` is written while notifications of Transfer data are not enabled |
| `0xFE` Procedure already in progress | `fetch` or `confirm` is written while a fetch is running |
| `0x05`, `0x0F` | The connection is not encrypted, see [open-session](open-session.md) |

| Case | Central writes | Sensor stick answers |
|---|---|---|
| Unknown op code | `7F` | `80 7F 01` |
