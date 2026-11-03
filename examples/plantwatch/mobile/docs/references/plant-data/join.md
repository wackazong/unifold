# join

Kind: command

```wit
join: func(token: string) -> result<_, command-failure>;
```

Pre: the session is `none` or `lost`.
Result: the phone acts for that owner. From `none`, the first exchange brings the owner's plants, alerts and history. From `lost`, the phone keeps its plants, its readings and its waiting changes, and the next exchange uploads them with the new token. A token that the server does not accept does not fail the command; it shows after the first exchange as the session `lost`.
Errors: `session exists` when the session is `active`; `store unusable`.
Examples:

| Case | Given | Expected |
|---|---|---|
| join | a token of an existing owner | the command returns; after the first exchange the owner's plants are on the phone |
| bad token | a token the server does not accept | the command returns; after the first exchange `session` is `lost` |
| rejoin | session `lost`, 3 readings waiting, a new token of the same owner | the command returns; after the next exchange `session` is `active` and the readings reach the server |
