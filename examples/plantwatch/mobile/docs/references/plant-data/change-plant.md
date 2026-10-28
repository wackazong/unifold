# change-plant

Kind: command

```wit
change-plant: func(plant-id: string, name: option<string>, lower-limits: option<limits>, sensor-id: option<option<string>>) -> result<_, command-failure>;
```

Pre: the session is `active`; the plant is on the phone; a given name has 1 to 60 characters; a given limit lies in the range of its quantity.
Result: the plant has the new values, `waiting`, and the change reaches the server in the order it was made. "sensor id: none" releases the sensor stick from the plant; readings already in the history stay. An observer of "plants" gets the plant within 1 second.
Errors: `no session`, `invalid` with the field, `unknown plant`, `sensor stick in use`, `store unusable`.
Examples:

| Case | Given | Expected |
|---|---|---|
| offline change | no network; the lower limit of soil moisture is set to 25 | the command returns; "get plant" shows 25 and `waiting`; an observer of "plants" gets the plant within 1 second |
| change confirmed | the next exchange succeeds | the plant is `in step`; "changes waiting" is 0 |
| change refused | the server no longer has the plant | the plant is `refused` with `removed elsewhere` |
| limit out of range | a lower limit of 120 for soil moisture | `invalid`, naming the limit; nothing changes |
