# change-plant

Kind: operation

```wit
change-plant: func(plant-id: string, name: option<string>, lower-limits: option<limits>, sensor-id: option<option<string>>) -> result<_, command-failure>;
```

Pre: the plant is on the phone; a given name has 1 to 60 characters; a given limit lies in the range of its quantity.
Result: the plant has the new values, `waiting`, and the change reaches the server in the order it was made. "sensor id: none" releases the sensor stick from the plant; readings already in the history stay. An observer of "plants" gets the plant within 1 second.
Errors: `no session`, `invalid` with the field, `unknown plant`, `sensor stick in use`, `store unusable`.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| offline change | no network | `change-plant` that sets the lower limit of soil moisture to 25 | ok; `plant` shows 25 and `waiting`; an observer of "plants" gets the plant within 1 second |
| change confirmed | the change of `offline change`, then an exchange that succeeded | `plant(id)` | the plant is `in step`; `changes-waiting` is 0 |
| change refused | the change of `offline change`, then an exchange in which the server no longer has the plant | `plant(id)` | the plant is `refused` with `removed elsewhere` |
| limit out of range | | `change-plant` with a lower limit of 120 for soil moisture | `invalid`, naming the limit; nothing changes |
