# Glossary of ble-client

Terms that have one fixed meaning inside this unit. Inherited terms are cited in [context.md](../explanation/context.md) and are not repeated here.

| Term | Meaning |
|---|---|
| Consumer | The one receiver that is attached to `sensor-readings` and takes the batches. |
| Acknowledge | The consumer tells the client that it has stored a batch. Never said of the radio. |
| Confirm | The client tells a sensor stick up to which sequence number its readings are safe. Never said of the consumer. |
| Chunk | The readings the client asks a sensor stick for in one request. One chunk becomes one batch, less the readings dropped as invalid. |
| Session | One attempt to fetch from one sensor stick, from its trigger to its end, across reconnects. In this unit the word never means the phone acting for an owner. |
| Trigger | An event that starts a session. |
| Time reference | A tick count of a sensor stick together with the phone's UTC time at the moment the client read it. |
| Anchor | A time reference the client keeps for one boot of a paired sensor stick. |
| Outcome | How a "fetch now" ended for one sensor stick. |
