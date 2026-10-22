# Energy budget

Where the charge of the cell goes, and how much each activity of the firmware may use. All figures are planned values. They are replaced by measured ones when a board exists.

## What is available

| Item | Value |
|---|---|
| Cell | CR2032, nominal 225 mAh |
| Usable under pulsed load down to 2.0 V | 170 mAh |
| Required life | 12 months, 8 760 h |
| Average current allowed | 170 mAh / 8 760 h = 19.4 µA |

## What is planned

At the default sampling interval of 900 s.

| Activity | Charge per event | Events per day | Average current |
|---|---|---|---|
| Sleeping with the tick counter running | | all the time | 2.0 µA |
| Taking and storing one reading | 600 µC | 96 | 0.7 µA |
| One advertising event | 12 µC | 67 237 | 9.3 µA |
| One connection with a fetch of a few hours of readings | 9 mC | 4 | 0.4 µA |
| **Sum** | | | **12.4 µA** |
| Reserve | | | 7.0 µA |

With 12.4 µA the cell lasts about 19 months. The reserve covers cold, ageing of the cell, and the difference between planned and measured values.

## What one event contains

| Event | Parts |
|---|---|
| Reading, 600 µC | Soil probe powered for 100 ms at 5 mA: 500 µC. Ambient sensor: 45 µC. Processor and converter: 40 µC. Writing the reading to memory, with the share of a block erase: 15 µC. |
| Advertising event, 12 µC | Three packets at 0 dBm, one per advertising channel, and the listening time after each |
| Connection, 9 mC | 3 s at an average of 3 mA: setting up, encryption, about 100 readings, confirm |

## How the figures move

| Change | Effect on the average current |
|---|---|
| Sampling interval 300 s instead of 900 s | + 1.3 µA |
| Advertising interval 1000 ms instead of 1285 ms | + 2.7 µA |
| Advertising interval 2000 ms instead of 1285 ms | − 3.3 µA |
| One more connection of 3 s per day | + 0.1 µA |
| A central that stays connected at a 50 ms interval for one hour a day | + 6 µA |
| A second measurement per reading | + 0.6 µA |

## Limits that follow

- The advertising interval is not shorter than 1 s.
- A reading powers the soil probe once.
- A connection without requests is closed after 30 s.
- Any change that adds more than 1 µA is a decision of this unit.
