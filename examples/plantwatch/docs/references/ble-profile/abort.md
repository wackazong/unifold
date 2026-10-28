# abort

Kind: command

```text
write Transfer control (0005):  03                                                   length 1
indicate Transfer control:      80 03 <result code>                                  length 3
```

Pre: the connection is encrypted; indications of Transfer control are enabled. `abort` is accepted at any time.
Result: a running fetch ends: the sensor stick stops sending and indicates a fetch result with the result code `aborted` and the true `sent` and `last`; the central may confirm what it has received. Without a running fetch it does nothing and its result is `success`.
Errors: ATT errors `0x05` and `0x0F` over an unencrypted connection; `0xFD` when indications are not enabled.
Examples:

| Case | Central writes | Sensor stick answers |
|---|---|---|
| Abort without a fetch | `03` | `80 03 00` |
| Abort after 10 records of a fetch of 96 | `03` | No further record; `80 01 04 0A 00 70 12 00 00 01`, then `80 03 00` |
