# Glossary of sync

Terms that have one fixed meaning inside this unit. Inherited terms are
cited in [context.md](../context.md) and are not repeated here.

| Term | Meaning |
|---|---|
| Query | A read of `plant-data`. It answers from the store and never from the network. |
| Observer | Whoever asked for a query in its "observe" form and gets the answer again when it changes. |
| Command | A call of `plant-data` that changes something on the phone. |
| Upload state | Where a reading stands with the server: `fetched`, `confirmed` or `refused` ([local-store.md](local-store.md)). |
| Waiting change | The settings of one plant that the owner changed and the server has not confirmed yet. |
| Refusal | The server's answer that a change of a plant is wrong and will not be accepted when sent again. |
| Binding | The fact that a sensor stick belonged to a plant from one time to another. |
| Pause | The time after a failed exchange in which sync sends no request ([exchange.md](exchange.md)). |
| Acknowledge | sync tells the source of a batch that it has stored the batch durably. |
