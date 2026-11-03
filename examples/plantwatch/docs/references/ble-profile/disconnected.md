# disconnected

Kind: event

```text
the connection ends; the central's Bluetooth stack reports it with its reason
```

The connection ends, whichever side ends it:

| Cause | Who ends it |
|---|---|
| The central has what it came for, or gives up | The central disconnects |
| No ATT request for 30 s | The sensor stick may disconnect |
| The connection is 10 minutes old | The sensor stick may disconnect |
| No packet arrives within the supervision timeout of 4 s | The radio link breaks; both sides notice |

After the event, the sensor stick advertises again within 1 s. A central that has received records but not confirmed them confirms them in its next connection; the sensor stick has kept them.
