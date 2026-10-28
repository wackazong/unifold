# token-for-another-phone

Kind: command

```wit
token-for-another-phone: func() -> result<string, command-failure>;
```

Pre: the session is `active`; a network connection exists.
Result: a further token for the same owner, obtained from the server.
Errors: `network needed` when there is no answer from the server; `no session`; `store unusable`.
Examples:

| Case | Given | Expected |
|---|---|---|
| online | a network connection | a token that "join" on another phone accepts |
| offline | no network connection | `network needed` |
