# get-state

Kind: query

```http
GET /state
```

Pre: none.
Result: `200` with the [state](emulator-state.md) object.
Errors: `404` `not_found` for an unknown path; `405` `method_not_allowed` for another method.
Examples:

| Case | Request | Expected |
|---|---|---|
| at start | `GET /state` | `200`; `scenario` is `steady`, `rate` 1, `link.advertising` `true` |
| after one day | `GET /state` after `PUT /time` with `{"elapsed_s": 86400}` on `drying-out` | `200`; the state object shown in [state](emulator-state.md) |
