# confirm

Kind: command

```text
write Transfer control (0005):  02 <up_to: 4 bytes>                                  length 5
indicate Transfer control:      80 02 <result code> <count: 2> <oldest: 4>           length 9
```

Pre: the connection is encrypted; indications of Transfer control are enabled; no fetch is running; `up_to` is at most the newest reading taken. The central holds every reading the sensor stick sent up to `up_to`, normally `last` of the fetch result.
Result: the sensor stick marks every stored reading with a sequence number of at most `up_to` as delivered; such a reading is not sent again and its space may be reused; the mark survives a restart of the sensor stick. The result carries `count`, the number of stored readings afterwards, and `oldest`, the sequence number of the oldest stored reading afterwards, 0 if none. `confirm` is cumulative: it covers all readings up to `up_to`, including readings the central has never fetched. A `confirm` with an `up_to` at or below an earlier one succeeds and changes nothing. A `confirm` is valid in any connection: a central that lost the connection after storing confirms in the next connection without fetching again, and a central that lost the connection before the confirm result arrived sends the same `confirm` again in the next connection, whether the sensor stick had carried it out or not.
Errors: `out-of-range` when `up_to` is above the newest reading taken; nothing changes, the central has made an error, reads Status and starts over. `storage-failure` when the sensor stick cannot mark its stored readings; nothing changes, the central disconnects and retries later. ATT error `0xFE` while a fetch is running; `0xFD`, `0x05` and `0x0F` as for `fetch`.
Examples: a sensor stick stores the 96 readings 4711 to 4806 and has taken none after them; each case starts from this state.

| Case | Central writes | Sensor stick answers |
|---|---|---|
| Confirm up to 4720 | `02 70 12 00 00` | `80 02 00 56 00 71 12 00 00`: 86 stored, oldest 4721 |
| The same confirm again | `02 70 12 00 00` | The same result. Nothing changes. |
| Confirm everything | `02 C6 12 00 00` | `80 02 00 00 00 00 00 00 00` |
| Confirm above the newest | `02 C7 12 00 00` | `80 02 03 00 00 00 00 00 00`. Nothing changes. |
