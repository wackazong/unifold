# get-readings

Kind: query

```http
GET /readings?from=<lowest sequence number, default 0>&limit=<at most 5000, default 1000>
```

Pre: `limit` is at most 5000.
Result: `200` with the readings taken since the scenario was loaded, from sequence number `from`:

```json
{
  "readings": [
    {
      "sequence_number": 1,
      "boot_counter": 1,
      "seconds_since_boot": 0,
      "elapsed_s": 0,
      "soil_moisture": 60.0,
      "light": 0,
      "temperature": 21.4,
      "state": "stored"
    }
  ],
  "more": false
}
```

A quantity that is absent in a reading has no member. `state` is `stored`, `delivered` (covered by a confirm) or `overwritten` (discarded to make room before any confirm). `more` is `true` when readings with a higher sequence number exist.
Errors: `400` `invalid_request` when a query parameter is unknown, has the wrong type or is out of range.
Examples:

| Case | Request | Expected |
|---|---|---|
| the first reading | `GET /readings?limit=1` right after `drying-out` was loaded | `200`; one reading, sequence number 1, `soil_moisture` 60.0, `state` `stored`, `more` `false` |
| after an overflow | `GET /readings?limit=1` after 2 881 readings without a confirm | `200`; reading 1 with `state` `overwritten`, `more` `true` |
| limit too large | `GET /readings?limit=5001` | `400` `invalid_request` |
