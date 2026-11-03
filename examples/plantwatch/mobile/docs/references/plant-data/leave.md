# leave

Kind: command

```wit
leave: func() -> result<_, command-failure>;
```

Pre: the session is not `none`; in the session `active`, a network connection exists.
Result: `left`: in the session `active`, what is waiting is uploaded first; then plants, readings, alerts and the token are removed from the phone. In the session `lost`, nothing is uploaded: readings that the server has not confirmed are removed with the rest, and `readings-waiting` of the last exchange state said how many.
Errors: `network needed` when the session is `active` and there is no answer from the server; `no session`; `store unusable`.
Examples:

| Case | Given | Expected |
|---|---|---|
| leave | 3 readings waiting; a network connection | the readings reach the server; then the phone holds no plant and the session is `none` |
| leave a lost session | session `lost`, 3 readings waiting, no network connection | the phone holds no plant and no reading, and the session is `none` |
