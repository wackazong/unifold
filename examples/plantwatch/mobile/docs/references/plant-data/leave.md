# leave

Kind: command

```wit
leave: func() -> result<_, command-failure>;
```

Pre: the session is not `none`; a network connection exists.
Result: `left`: what is waiting is uploaded, then plants, readings, alerts and the token are removed from the phone.
Errors: `network needed` when there is no answer from the server; `no session`; `store unusable`.
Examples:

| Case | Given | Expected |
|---|---|---|
| leave | 3 readings waiting; a network connection | the readings reach the server; then the phone holds no plant and the session is `none` |
