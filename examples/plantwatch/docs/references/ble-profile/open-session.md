# open-session

Kind: operation

```text
1. connect to the advertising sensor stick
2. read Info; disconnect and write nothing if major > the highest major the central implements
3. start encryption; without a bond, bond first (LE Secure Connections, Just Works)
4. optionally exchange the ATT MTU
5. enable the indications and notifications needed
```

Pre: the sensor stick advertises and no central is connected to it. A new bond is accepted only while bonding is open: for 5 minutes after the sensor stick starts; a user opens bonding by restarting the sensor stick, that is by taking out and putting back the cell. The central may skip steps 3 to 5 if it only wants Info and Status.
Result: a connection, encrypted after step 3, with the descriptors the central enabled. The connection parameters:

| Property | Value |
|---|---|
| Connections at a time | 1. While connected, the sensor stick does not advertise. |
| Connection interval | The central chooses. The sensor stick accepts 15 ms to 100 ms and may request 30 ms to 50 ms. |
| Peripheral latency | 0 during a fetch. Otherwise the sensor stick may request up to 4. |
| Supervision timeout | 4 s |
| ATT MTU | The sensor stick accepts an MTU exchange and supports at least 67 bytes. It works with 23. |
| Idle disconnect | The sensor stick may disconnect when the central has sent no ATT request for 30 s. |
| Longest connection | The sensor stick may disconnect a central after 10 minutes. |

A central disconnects as soon as it has what it came for. A sensor stick lives on a coin cell, and every second of connection costs it energy. "Bonding" here means BLE pairing with storage of the keys; it binds a sensor stick and a central, not a plant. The central starts it after connecting; the sensor stick sends no security request. A sensor stick keeps at least 4 bonds, which survive a restart; when all bond places are taken, a new bond replaces the bond that was used longest ago. Just Works does not protect against an attacker who is active during the 5 minutes in which bonding is open.
Errors: outside the bonding time the sensor stick rejects pairing requests of unknown centrals with `Pairing Not Supported`. A request on an attribute that needs an encrypted connection over an unencrypted connection fails with the ATT error `Insufficient Authentication` (`0x05`) when no bond exists and `Insufficient Encryption` (`0x0F`) when one exists; which attributes need encryption is listed in [reading-service](reading-service.md).
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| Pairing after the window | the sensor stick started 301 s ago | an unknown central starts pairing in step 3 | rejected with `Pairing Not Supported` |
| No bond, no encryption | the central has no bond and skipped step 3 | a write to Transfer control | ATT error `0x05` |
| Bonded, encryption not yet on | the central has a bond and step 3 has not run yet | a write to Transfer control | ATT error `0x0F` |
| A fifth bond | the sensor stick keeps 4 bonds and bonding is open | a fifth central bonds | its bond replaces the one that was used longest ago |
| Higher major version | the sensor stick reports `major` 2 and the central implements only 1 | the central reads Info in step 2 | it disconnects and writes nothing |
