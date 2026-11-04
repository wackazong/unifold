# Runtime of plantwatch

Stories that cross several parts and that no single part can tell are scenarios in the `unifold.yaml` of the lowest unit that contains every part they name; the checker follows every hop through the wiring and the contracts, and `unifold scenario UNIT NAME` draws a scenario as a sequence diagram. The scenarios of plantwatch include those of its parts, so that the whole story is drawn at the root. Which parts exist is in the [component diagram](../diagrams/component.md).

## The path of a reading

The way of a reading from the pot to the owner is told in four scenarios of plantwatch, each drawn by `unifold scenario . NAME` at the root:

| Scenario | Story | Told by |
|---|---|---|
| `take-a-reading` | the sensor stick wakes, measures, stores the reading and sleeps again | `device` |
| `fetch-readings` | a phone comes into range, fetches the stored readings, stores them and confirms them; `serve-a-fetch` of `device` is the same connection seen from the sensor stick | `mobile` |
| `upload-and-alert` | the phone uploads, the server opens an alert, the owner is notified once and sees the plant first in the list | plantwatch, with `upload-leads-to-alert` of `cloud` and `an-alert-arrives` of `mobile` |
| `first-plant` | an owner starts the app, adds a plant and pairs a sensor stick | `mobile` |

Two more scenarios tell how the parts are exercised and run: `end-to-end-alert-test`, the rig driving the simulated sensor stick through a dry spell, and `start-the-server-side`, the container host starting the services, told by `cloud`.

What holds along the whole path: a reading is taken at the sampling interval whether or not a phone is near; the phone confirms to the sensor stick only what it has stored; the server answers an upload before it has judged the reading; and the owner's phone learns about an alert through the push service and through the next exchange, whichever comes first.
