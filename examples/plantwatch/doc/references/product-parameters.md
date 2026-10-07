# Product parameters

The numbers plantwatch version 1 is designed for. Units that depend on one of
them cite it in their own context file. The terms are defined in the
[glossary](glossary.md).

| Parameter | Value | Why it matters |
|---|---|---|
| Sampling interval | 15 minutes by default, adjustable from 5 to 60 minutes | Sets energy use, storage need and how fresh an alert can be |
| Battery life of a sensor stick | At least 12 months on one CR2032 cell at the default interval | Limits radio time and wake time per reading |
| Readings kept on a sensor stick | At least 30 days at the default interval, that is 2 880 readings | The phone may be away that long without loss |
| Behaviour when the sensor stick is full | The oldest undelivered reading is overwritten | Recent state matters more than old history |
| Sensor sticks per phone | Up to 20 | Bounds scan and fetch time in the app |
| Plants per owner | Up to 50 | Bounds list sizes in API and app |
| Time from upload to notification | Under 1 minute | The server side must evaluate readings as they arrive |
| History kept on the server | 2 years per plant | Bounds storage |
| History kept on the phone | 90 days per plant | The app works offline within this window |
| Radio protocol version | 1 | Parts state the versions they support |
