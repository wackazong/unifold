# Runtime of plantwatch

Stories that cross several parts and that no single part can tell are scenarios in the `unifold.yaml` of the lowest unit that contains every part they name; the checker follows every hop through the wiring and the contracts, and the explorer draws each as a sequence diagram. The root holds two of them: `upload-and-alert`, which includes scenarios of `cloud` and `mobile`, so that its whole story is drawn at the root, and `an-interrupted-fetch-loses-nothing`.

## The path of a reading

The way of a reading from the pot to the owner is told in four scenarios, each held by the unit in the last column:

| Scenario | Story | Told by |
|---|---|---|
| `start-and-first-reading` | the sensor stick starts, measures, stores the reading and sleeps until the next one | `device` |
| `fetch-and-upload` | a phone comes into range, fetches the stored readings, stores them, confirms them and uploads them; `serve-a-fetch` of `device` is the same connection seen from the sensor stick | `mobile` |
| `upload-and-alert` | the server opens an alert for an uploaded reading, the owner is notified once and sees the plant first in the list | plantwatch, with `upload-leads-to-alert` of `cloud` and `an-alert-arrives` of `mobile` |
| `first-plant` | an owner starts the app, adds a plant and pairs a sensor stick | `mobile` |

Two more scenarios tell how the parts are exercised and run: `an-interrupted-fetch-loses-nothing`, the rig cutting a fetch from the simulated sensor stick and finding every reading in the history once, and `the-server-side-starts-again`, the services taking up their work after a stop, told by `cloud`. The other scenarios are in the `unifold.yaml` of `device`, `mobile`, `cloud` and `cloud/services/alerts`.

What holds along the whole path: a reading is taken at the sampling interval whether or not a phone is near; the phone confirms to the sensor stick only what it has stored; the server answers an upload before it has judged the reading; and the owner's phone learns about an alert through the push service and through the next exchange, whichever comes first.
