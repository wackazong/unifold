# token-for-another-phone

Kind: command

```wit
token-for-another-phone: func() -> result<string, command-failure>;
```

Pre: a network connection exists.
Result: a further token for the same owner, obtained from the server.
Errors: `network needed` when there is no answer from the server; `no session`; `store unusable`.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| online | a network connection | `token-for-another-phone()` | a token that "join" on another phone accepts |
| offline | no network connection | `token-for-another-phone()` | `network needed` |
