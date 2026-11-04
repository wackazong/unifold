# get-state

Kind: query

```http
GET /state
```

Pre: none.
Result: `200` with the [state](emulator-state.md) object.
Errors: `404` `not_found` for an unknown path; `405` `method_not_allowed` for another method. The body of an error response is an [error](control-error.md) object.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| at start | the program has just started | `GET /state` | `200`; `scenario` is `steady`, `rate` 1, `link.advertising` `true` |
| after one day | `PUT /time` with `{"elapsed_s": 86400}` on `drying-out` was answered | `GET /state` | `200`; the state object shown in [state](emulator-state.md) |
