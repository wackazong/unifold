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
| Attached | A sensor stick is attached to a plant when the server side knows that its readings belong to that plant: the plant names its sensor id. A sensor stick is attached to at most one plant. Attaching is the plant half of pairing. |
| Threshold | A limit for one measured quantity of a plant, below or above which the plant needs attention. |
| Alert | The state "this plant needs attention for this reason". It opens once, stays open while the reason lasts, and closes. |
| Notification | A message to the owner about an alert that has opened. One per alert. |
| Scenario | A scripted course of sensor values over simulated time, used instead of real hardware. |
| Batch | A group of readings of one sensor stick that is transferred together. |
| Record | The binary form of one reading, as it crosses the radio link. |
| Holder | Anything that keeps or passes on a reading after it has left the sensor stick. |
| Bonding | BLE pairing with storage of the keys. It binds a sensor stick and a central, never a plant. |
| Stored | Of a reading on a sensor stick: taken, and neither covered by a confirm nor discarded. |
| Fetch | The request with which a central has stored readings sent to it. It changes nothing. |
| Confirm | The request with which a central states that it holds every reading up to a sequence number. Only a confirm releases readings. |
| Overflow | A sensor stick discarding its oldest stored readings to make room for new ones. |
| Time reference | A tick count of a sensor stick together with the UTC time at which a central read it. |
| Live reading | The newest reading, sent to a connected central at the moment it is taken. |
| Quantity | One measured value of a reading: soil moisture, light or temperature. |
