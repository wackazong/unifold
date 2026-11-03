# session-lost

Kind: event

```wit
session-lost: func(reason: string);
```

The server refused the token of the phone at an exchange, and the session is now `lost`. The reason is `token not accepted`, as `last-failure` of [exchange-state](exchange-state.md) shows it. The plants, readings and alerts stay on the phone and stay readable. Nothing is exchanged until the phone joins the owner again with `join`, or leaves it with `leave`.
