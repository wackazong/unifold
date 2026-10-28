# command-failure

Kind: type

```wit
variant command-failure {
  no-session, session-exists, network-needed, invalid(string), limit-reached,
  unknown-plant, sensor-stick-in-use, store-unusable
}
```

| Failure | Commands | Meaning |
|---|---|---|
| `no session` | all but "start" and "join" | the session is `none` |
| `session exists` | start, join | the phone already acts for an owner; "leave" comes first |
| `network needed` | token for another phone, leave | no answer from the server |
| `invalid` | create plant, change plant | name empty or longer than 60 characters, or a limit outside the range of its quantity; with the field |
| `limit reached` | create plant | the owner has 50 plants |
| `unknown plant` | change, remove, dismiss | no plant with this id on the phone |
| `sensor stick in use` | create plant, change plant | the sensor id is attached to another plant on this phone |
| `store unusable` | all, and all queries | the store on the phone was written by a newer version of the program |
