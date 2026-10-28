# join

Kind: command

```wit
join: func(token: string) -> result<_, command-failure>;
```

Pre: the session is `none`.
Result: the phone acts for that owner. The first exchange brings the owner's plants, alerts and history. A token that the server does not accept does not fail the command; it shows after the first exchange as the session `lost`.
Errors: `session exists`, `store unusable`.
Examples:

| Case | Given | Expected |
|---|---|---|
| join | a token of an existing owner | the command returns; after the first exchange the owner's plants are on the phone |
| bad token | a token the server does not accept | the command returns; after the first exchange `session` is `lost` |
