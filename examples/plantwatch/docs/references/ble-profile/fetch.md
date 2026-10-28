# fetch

Kind: command

```text
write Transfer control (0005):  01 <first: 4 bytes> <limit: 2 bytes>                  length 7
notify Transfer data (0006):    one or more whole records, one after the other, no header
indicate Transfer control:      80 01 <result code> <sent: 2> <last: 4> <more: 1>       length 10
```

Pre: the connection is encrypted; indications of Transfer control and notifications of Transfer data are enabled; no fetch is running. The central uses Write Request, not Write Command. `first` is the lowest sequence number the central wants; 0 or any number below `oldest` means "from the oldest stored reading". `limit` bounds the number of records; 0 means no limit.
Result: the sensor stick sends the stored readings with a sequence number of at least `first`, in ascending order, as records on Transfer data, then indicates the fetch result: `sent`, the number of records sent; `last`, the sequence number of the last record sent, 0 if none; `more`, 1 if stored readings with a higher number remain, else 0. A fetch changes nothing on the sensor stick; only a confirm does. The sensor stick sends a reading that it takes during a fetch only if its sequence number is within `limit`; `more` tells the central about the rest. A fetch with nothing to send succeeds with `sent` 0, `last` 0 and `more` 0. The records are in the binary form of the [reading schema](../reading-schema.md); each starts with its own length. A sensor stick never splits a record across notifications; a notification holds at most as many records as fit into ATT MTU minus 3 bytes, with the default MTU of 23 that is one record of version 1.0; records of one fetch arrive in ascending order of sequence number; a sensor stick sends Transfer data only between a `fetch` request and its result. The central compares `sent` with the number of records it received; if they differ, it discards nothing it has, confirms nothing, and fetches again. The central stores the received readings so that they survive its own failure, then confirms with [confirm](confirm.md); if `more` was 1, it repeats the fetch with `first` set to `last` + 1.
Errors: the result codes of [transfer-result](transfer-result.md), and the ATT errors `0xFD` when indications of Transfer control or notifications of Transfer data are not enabled, `0xFE` while a fetch is running, `0x05` and `0x0F` over an unencrypted connection. When something fails:

| Event | Sensor stick | Central |
|---|---|---|
| Connection is lost during a fetch | Ends the fetch. Changes no stored reading. | Keeps the complete records it has received. Reconnects later and fetches from its last stored sequence number + 1, or from 0. |
| Central writes `abort` | Stops sending and indicates a fetch result with the result code `aborted` and the true `sent` and `last` | May confirm what it has received |
| Sensor stick cannot read its stored readings | Result `storage-failure`, changes nothing | Disconnects and retries later; does not confirm |
| A record is longer than ATT MTU minus 3 | Result `mtu-too-small`, sends no record | Exchanges a larger MTU and fetches again |
| Central receives a record it must reject | Nothing | Drops that record, keeps the others, and still confirms up to `last` |

Examples: a sensor stick stores the 96 readings 4711 to 4806 and has taken none after them; each case starts from this state; values are bytes on Transfer control, in hexadecimal.

| Case | Central writes | Sensor stick answers |
|---|---|---|
| Fetch everything | `01 00 00 00 00 00 00` | 96 records, then `80 01 00 60 00 C6 12 00 00 00` |
| Fetch with a limit of 10 | `01 00 00 00 00 0A 00` | Records 4711 to 4720, then `80 01 00 0A 00 70 12 00 00 01` |
| Fetch above the newest | `01 C7 12 00 00 00 00` | No record, `80 01 00 00 00 00 00 00 00 00` |
| Request too short | `01 00 00` | `80 01 02 00 00 00 00 00 00 00` |
| Fetch during a fetch | `01 00 00 00 00 00 00` | ATT error `0xFE`, no indication |
| Fetch, Transfer data not enabled | `01 00 00 00 00 00 00` | ATT error `0xFD`, no indication |
