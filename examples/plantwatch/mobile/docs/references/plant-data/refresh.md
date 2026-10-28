# refresh

Kind: command

```wit
refresh: func() -> exchange-state;
```

Pre: the session is not `none`.
Result: asks for a fetch from sensor sticks in range and runs an exchange now; returns the exchange state after the attempt.
Errors: none as a failure of the call; `last-failure` of the returned state says why an exchange did not succeed.
Examples:

| Case | Given | Expected |
|---|---|---|
| offline | no network connection | the state with `last-failure` `no network`; readings and changes stay waiting |
