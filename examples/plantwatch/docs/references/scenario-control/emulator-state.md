# emulator-state

Kind: type

```json
{
  "scenario": "drying-out",
  "elapsed_s": 86400,
  "rate": 0,
  "tick": {"boot_counter": 1, "seconds_since_boot": 86400},
  "sampling_interval_s": 900,
  "readings_taken": 97,
  "stored": {"count": 97, "oldest": 1, "newest": 97},
  "confirmed_up_to": 0,
  "overflow": false,
  "link": {
    "in_range": true,
    "advertising": true,
    "connected": false,
    "bonds": 0,
    "bonding_open": false,
    "drop_fetch_after": null
  }
}
```

The state object, as `drying-out` shows it one simulated day after it was loaded.

| Member | Meaning |
|---|---|
| `scenario` | name of the loaded scenario; at start it is the built-in scenario `steady`, running at rate 1 |
| `elapsed_s` | simulated seconds since the scenario was loaded |
| `rate` | simulated seconds per real second; 0: time stands still |
| `tick` | the tick count of the simulated sensor stick |
| `readings_taken` | number of readings taken since the scenario was loaded |
| `stored` | readings taken and not confirmed: their number, and the lowest and highest sequence number, each 0 if none |
| `confirmed_up_to` | highest sequence number a central has confirmed, 0 if none |
| `overflow` | `true` if a stored reading has been overwritten since the last confirm or restart |
| `link.in_range` | as set with `PUT /link` |
| `link.advertising`, `link.connected` | what the radio side is doing now |
| `link.bonds` | number of centrals that have bonded |
| `link.bonding_open` | `true` while a new bond is accepted |
| `link.drop_fetch_after` | as set with `PUT /link`, `null` once it has taken effect |
