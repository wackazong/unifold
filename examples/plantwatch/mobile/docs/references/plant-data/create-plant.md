# create-plant

Kind: command

```wit
create-plant: func(name: string, lower-limits: limits, sensor-id: option<string>) -> result<string, command-failure>;
```

Pre: the session is `active`; fewer than 50 plants exist; the name has 1 to 60 characters; every limit lies in the range of its quantity; the sensor id is attached to no other plant on this phone.
Result: the plant id. The plant exists on the phone, `waiting`, and reaches the server without further calls.
Errors: `no session`; `invalid` with the field, when the name is empty or longer than 60 characters or a limit is outside the range of its quantity; `limit reached` when the owner has 50 plants; `sensor stick in use`; `store unusable`.
Examples:

| Case | Given | Expected |
|---|---|---|
| 51st plant | 50 plants exist | `limit reached` |
| before "start" | the session is `none` | `no session` |
| sensor stick in use | the sensor id of "Monstera" | `sensor stick in use` |
