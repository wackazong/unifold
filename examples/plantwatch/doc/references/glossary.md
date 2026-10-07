# Glossary

The terms of plantwatch. Every unit uses them with this meaning.

| Term | Meaning |
|---|---|
| Plant | A plant the user has registered, with a name and thresholds. |
| Owner | The user a plant belongs to. A plant has one owner. |
| Sensor stick | The hardware device that sits in the pot of one plant. |
| Sensor id | The unchangeable identifier of a sensor stick. |
| Reading | One set of measurements taken at the same moment by one sensor stick: soil moisture, light and temperature, with a sequence number and a time. Never a single value. |
| Sequence number | A number the sensor stick gives to each reading, strictly increasing, never reused. |
| Sampling interval | The time between two readings of a sensor stick. |
| Tick count | The sensor stick's own measure of time: a boot counter and the seconds since that boot. |
| Central | The BLE role of the side that connects to a sensor stick, normally a phone. |
| Pairing | Binding a sensor stick to a phone and to a plant. |
| Attached | A sensor stick is attached to a plant when the server side knows that its readings belong to that plant. Attaching is the plant half of pairing. |
| Threshold | A limit for one measured quantity of a plant, below or above which the plant needs attention. |
| Alert | The state "this plant needs attention for this reason". It opens once, stays open while the reason lasts, and closes. |
| Notification | A message to the owner about an alert that has opened. One per alert. |
| Scenario | A scripted course of sensor values over simulated time, used instead of real hardware. |
| Batch | A group of readings of one sensor stick that is transferred together. |
