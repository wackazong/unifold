# start

Kind: command

```wit
start: func() -> result<_, command-failure>;
```

Pre: the session is `none`. Needs no network connection.
Result: the phone acts for a new owner. The server creates the owner at the first exchange.
Errors: `session exists` when the phone already acts for an owner; "leave" comes first. `store unusable`.
Examples:

| Case | Given | Expected |
|---|---|---|
| first start | the session is `none`; no network | the command returns; `session` is `active`, `owner-id` is none until the first exchange |
| already started | the session is `active` | `session exists` |
