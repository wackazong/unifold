# Radio behaviour of the device

The behaviour of the firmware of the sensor stick that a central sees over the air, and the limits of its memory and battery, as the firmware keeps them.

| Topic | Fact |
|---|---|
| Advertising | Every 1285 ms while no central is connected; it carries the newest sequence number and whether stored readings wait, and follows a change within 2 s |
| Notifications | A subscribed central is notified of every new reading within one connection interval |
| Status | The tick count in Status is the tick count of the read request itself |
| Confirm | A confirm result is indicated only after the mark is durable, so `success` survives power loss |
| Throughput | At the default ATT MTU one reading per notification; at least 40 readings per second to a central that takes 4 notifications per connection event at 100 ms or less; 2 880 readings in at most 72 s |
| Failing sensor | A sensor that fails leaves its quantity absent, and the reading is still taken |
| Sequence numbers | They rise strictly over the life of a sensor stick; they are consecutive between starts, with a jump at every start |
| Boot counter | It never repeats |
| Time | The seconds are wrong by at most 50 ppm, about 2 minutes in 30 days |
| Retention | At least 2 880 unconfirmed readings are kept through power loss and a change of the cell |
| Full memory | The oldest readings are discarded, up to 204 at once, and the overflow is reported |
| Battery | At least 12 months on one CR2032 cell at the default interval with 4 connections of 3 s a day |
| Starts | Readings for 16 383 starts |
