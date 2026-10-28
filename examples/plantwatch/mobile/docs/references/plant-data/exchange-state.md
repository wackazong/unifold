# exchange-state

Kind: query

```wit
exchange-state: func() -> exchange-state;
observe-exchange-state: func(observer: exchange-observer);
record exchange-state {
  session: session,
  owner-id: option<string>,
  last-exchange: option<string>,
  running: bool,
  readings-waiting: u32,
  changes-waiting: u32,
  last-failure: option<string>,
}
enum session { none, active, lost }
```

Pre: none.
Result: the state of the exchange with the server:

| Field | Content |
|---|---|
| session | `none`: the phone acts for no owner yet, and every other command fails. `active`. `lost`: the server no longer accepts the token; the data stays on the phone and stays readable, and nothing is exchanged until the phone joins the owner again. |
| owner-id | the owner the phone acts for; none until the server has created the owner |
| last-exchange | UTC time of the last exchange with the server that succeeded, or none |
| running | whether an exchange is running now |
| readings-waiting | number of readings the server has not confirmed |
| changes-waiting | number of plants in the state `waiting` |
| last-failure | `no network`, `server unavailable`, `token not accepted` or none |

Errors: none.
Examples:

| Case | Given | Expected |
|---|---|---|
| change confirmed | an offline change, then an exchange that succeeds | `changes-waiting` is 0 |
| token not accepted | the server refuses the token at an exchange | `session` is `lost`, `last-failure` is `token not accepted` |
