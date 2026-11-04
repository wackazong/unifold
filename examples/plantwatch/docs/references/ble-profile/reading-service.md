# reading-service

Kind: type

```text
7077xxxx-9a1c-4e5b-b3a2-5d1f6c0e2a47
```

A sensor stick has exactly one instance of the Reading service, as a primary service. All UUIDs of the profile share one 128-bit base; the 16-bit part `xxxx` selects the attribute:

| `xxxx` | Characteristic | Properties | Encrypted connection | Value length |
|---|---|---|---|---|
| `0001` | Reading service | | | |
| `0002` | Info | Read | not required | 18 bytes |
| `0003` | Status | Read, Notify | not required | 17 bytes |
| `0004` | Live reading | Read, Notify | required | one record, or 0 bytes |
| `0005` | Transfer control | Write, Indicate | required | 1 to 20 bytes |
| `0006` | Transfer data | Notify | required | one or more records |

Every characteristic with Notify or Indicate has a Client Characteristic Configuration descriptor. A sensor stick resets these descriptors to 0 at every new connection, also for a bonded central. The base and the company identifier in the advertising data are placeholders. Values `0007` to `00ff` are reserved for characteristics of later minor versions.
