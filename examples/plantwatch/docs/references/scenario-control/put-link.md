# put-link

Kind: command

```http
PUT /link

{"in_range": <boolean, default true>, "drop_fetch_after": <integer or null, default null>}
```

Pre: none; members that are left out keep their value.
Result: `200` with the [state](emulator-state.md) object. `in_range` `false`: the program drops a connection at once and stops advertising, as if the sensor stick were out of radio range; sampling goes on. `drop_fetch_after`: the program drops the connection during the next fetch after it has sent this many records, without sending a fetch result; takes effect once.
Errors: `400` `invalid_request` when a member is unknown, has the wrong type or is out of range; `400` `invalid_json`. The state of the program is unchanged after an error.
Examples:

| Case | Request | Expected |
|---|---|---|
| out of range | `PUT /link` with `{"in_range": false}` while a central is connected | `200`; `link.connected` and `link.advertising` `false`; time and sampling are untouched |
| a cut fetch | `PUT /link` with `{"in_range": true, "drop_fetch_after": 10}`, then a central fetches | the central gets 10 records and no fetch result; afterwards `link.drop_fetch_after` is `null` and `stored.count` is as before |
