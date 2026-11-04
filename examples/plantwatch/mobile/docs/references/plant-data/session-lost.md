# session-lost

Kind: event

```wit
session-lost: func(reason: string);
```

When: the server refused the token of the phone at an exchange; the session is now `lost`.
Delivery: exactly once per loss of the session; no order.

The reason is `token not accepted`, as `last-failure` of [exchange-state](exchange-state.md) shows it. The plants, readings and alerts stay on the phone and stay readable. Nothing is exchanged until the phone joins the owner again with `join`, or leaves it with `leave`.
