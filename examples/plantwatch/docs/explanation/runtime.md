# Runtime of plantwatch

Stories that cross several parts and that no single part can tell are scenarios in `unifold.yaml`, where the checker follows every hop through the wiring and the generator draws them. Which parts exist is in the [component diagram](../diagrams/component.md).

## The path of a reading

The way of a reading from the pot to the owner is told in four scenarios, each drawn end to end:

| Scenario | Story |
|---|---|
| [take-a-reading](../diagrams/scenario-take-a-reading.md) | the sensor stick wakes, measures, stores the reading and sleeps again |
| [fetch-readings](../diagrams/scenario-fetch-readings.md) | a phone comes into range, fetches the stored readings, stores them and confirms them |
| [upload-and-alert](../diagrams/scenario-upload-and-alert.md) | the phone uploads, the server opens an alert, the owner is notified once and sees the plant first in the list |
| [first-plant](../diagrams/scenario-first-plant.md) | an owner starts the app, adds a plant and pairs a sensor stick |

Two more scenarios tell how the parts are exercised and run: [end-to-end-alert-test](../diagrams/scenario-end-to-end-alert-test.md), the rig driving the simulated sensor stick through a dry spell, and [start-the-server-side](../diagrams/scenario-start-the-server-side.md), the container host starting the services.

What holds along the whole path: a reading is taken at the sampling interval whether or not a phone is near; the phone confirms to the sensor stick only what it has stored; the server answers an upload before it has judged the reading; and the owner's phone learns about an alert through the push service and through the next exchange, whichever comes first.
