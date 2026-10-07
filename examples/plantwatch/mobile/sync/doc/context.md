# Context of sync

What this unit inherits from the levels above. This is the only file of the
unit that links upward. Each item is restated so that the unit can be
understood when the link is not available.

## From mobile

| Source | What it says | What it means here |
|---|---|---|
| [mobile/0001 The local store is the only source for the screens](../../doc/decisions/0001-the-local-store-is-the-only-source-for-the-screens.md) | Screens read only from a store on the phone. Fetched readings and server data both flow into it. The owner's changes go into the store first and to the server afterwards. | sync owns this store. Every query of `plant-data` answers from it, and every command writes to it before anything is sent. |
| [mobile/0002 Fetch when the system reports a paired sensor stick](../../doc/decisions/0002-fetch-when-the-system-reports-a-paired-sensor-stick.md) | In the background the app runs in short slots. A slot does fetch, store, confirm; uploading follows if run time is left, otherwise later. | Storing a batch is fast and comes first. An upload may be cut off at any moment and must be repeatable. |
| [mobile/0003 A reading gets its time before it is stored](../../doc/decisions/0003-a-reading-gets-its-time-before-it-is-stored.md) | A reading arrives with a UTC time and an estimated flag. Both never change. The tick count stays in the reading; nothing behind the fetch computes with it. | sync stores, uploads and returns time, flag and tick count as received and never recomputes anything. |
| [mobile: data model](../../doc/references/data-model.md) | Defines reading, plant with a lower and an upper limit per quantity and a change state (`in step`, `waiting`, `refused`), alert, session and the two ages of data, each with its origin. The phone learns of an alert only from the server. | The store holds these things. `plant-data` returns them with these names. sync computes no alert. |
| [mobile: platform limits](../../doc/references/platform-limits.md) | Design budget of 10 seconds per background wake-up. Later network work runs when the operating system chooses, possibly hours later. | The sizes and pauses in [exchange.md](references/exchange.md). |
| [mobile: data model, session](../../doc/references/data-model.md) | A phone acts for one owner, known by a token. The server creates the owner at the first exchange; a further phone joins with a token from the first. The app leaves an owner only after the server has confirmed every reading on the phone. | The commands "start", "join", "token for another phone" and "leave" of `plant-data`. "Leave" waits for the upload. |

## From plantwatch

| Source | What it says | What it means here |
|---|---|---|
| [plantwatch/0004 Immutable readings](../../../doc/decisions/0004-readings-are-immutable-and-identified-by-sensor-and-sequence.md) | A reading is identified by sensor id and sequence number and never changes. Receivers accept a reading they already have. | The store keeps one reading per pair; the first one stored stays. Uploads may repeat. |
| [Conventions: delivery](../../../doc/references/conventions.md) | A sender deletes an item only after the receiver has confirmed it. A receiver accepts an item it already has and reports success. | sync acknowledges a batch it has seen before. It removes a reading only after the server has confirmed it. |
| [Conventions: time](../../../doc/references/conventions.md) | Every time is UTC, written as RFC 3339 with `Z` and whole seconds. | The form of every time in the store and in `plant-data`. |
| [Conventions: HTTP ports](../../../doc/references/conventions.md) | JSON bodies, errors with `code` and `message`, a repeated successful request succeeds again. | What sync expects of `cloud-api`. |
| [Conventions: measured quantities](../../../doc/references/conventions.md) | Ranges: soil moisture 0 to 100 percent, light 0 to 100 000 lux, temperature -20 to 60 °C. | A threshold limit outside its range is refused by a command. |
| [Product parameters](../../../doc/references/product-parameters.md) | 90 days of history on the phone, up to 50 plants per owner and 20 sensor sticks per phone, sampling interval from 5 to 60 minutes. | Retention and size of the store: at most 20 × 90 days × 288 readings a day. |
| [Glossary](../../../doc/references/glossary.md) | Batch: readings of one sensor stick transferred together. Alert: a state that opens once and closes. Owner: the user a plant belongs to. | An upload is a batch in this sense. |
