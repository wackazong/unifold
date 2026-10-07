# Glossary of emulator

The terms that have one fixed meaning inside this unit. Terms of the whole
project, such as scenario, sensor stick, reading and central, are cited in
[context](../context.md) and not repeated here.

| Term | Meaning |
|---|---|
| Program | The emulator as a running process |
| Simulated sensor stick | What a central sees on the radio link: the sensor stick the program plays |
| Simulated time | The seconds since the scenario was loaded. They move only when a client moves them or sets a rate. |
| Real time | The time of the host. The radio side runs in it. |
| Rate | Simulated seconds per real second. 0 means that simulated time stands still. |
| Client | Whatever sends requests to the control API |
| Radio face | Everything a central can observe over BLE |
| Control face | The HTTP API that dictates values, time and faults. A sensor stick has no such thing. |
| Track | The course of one quantity over simulated time, as points in a scenario |
| Point | A time and a value in a track |
| Event | Something a scenario lets happen at a given time. Version 1 knows the restart. |
| Start | The moment a scenario is loaded, and every restart in it. The seconds since boot begin at 0. |
