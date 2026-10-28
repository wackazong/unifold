# live-reading

Kind: event

```text
notify Live reading (0004): one record in the binary form of the reading schema, or 0 bytes
```

The newest reading the sensor stick has taken, as one record in the binary form of the [reading schema](../reading-schema.md). The value has length 0 as long as the sensor stick has taken no reading since its start. The characteristic requires an encrypted connection.

1. The central enables notifications of Live reading.
2. The central may read Live reading at once to get the newest reading.
3. The sensor stick notifies each new reading at the moment it takes it.

A live reading is not removed from the sensor stick by being notified. The reading is the same one that a fetch delivers later, with the same sequence number; the central recognises it by its sequence number. A central that keeps live readings still confirms them only through `confirm`.

| Case | Expected |
|---|---|
| The sensor stick takes reading 4807 while a central has notifications on | One notification with the record of 4807; a later fetch delivers 4807 again |
| A central reads Live reading before the first reading of this start | A value of 0 bytes |
