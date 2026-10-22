# Glossary of device

The terms that have one fixed meaning in the firmware and in all its parts. Terms of the whole project, such as reading, sequence number, tick count and central, are cited in [context](../explanation/context.md) and not repeated here.

| Term | Meaning |
|---|---|
| Board | The circuit board of the sensor stick with its microcontroller. What the firmware runs on. |
| Cell | The CR2032 coin cell that powers the board |
| Start | The firmware beginning to run, after the cell was put in or after a reset. Waking from sleep is not a start. |
| Boot counter | The number of starts of a board so far. The first part of the tick count. |
| Event | An alarm or an occurrence on the radio that wakes the board. The firmware runs only inside events. |
| Alarm | A second of the tick count at which a part has asked to be called |
| Part | One of the libraries the firmware is composed of |
| Raw value | A number as a sensor delivers it, before calibration |
| Block | A piece of durable memory that can only be erased as a whole |
| Stored | Of a reading: in durable memory, and neither delivered nor discarded |
| Delivered | Of a reading: covered by a confirm of a central. Only then is its room given up on purpose. |
| Mark | The sequence number up to which readings are delivered |
| Overflow | Discarding the oldest stored readings because durable memory is full |
| Substitute | Code that stands in for a part on a development machine |
