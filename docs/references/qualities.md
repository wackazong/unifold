# Qualities of a connection

What a connection promises beyond its parts, as the `## Qualities` section of its [contract](contracts.md) states it.

`## Qualities` holds what the connection promises beyond its parts, as a table `Aspect | Guarantee`, one row per aspect:

```markdown
## Qualities

| Aspect | Guarantee |
|---|---|
| latency | an upload of 500 readings is answered within 200 ms |
| throughput | 200 messages per second per topic |
| concurrency | one call at a time per session |
| delivery | at least once, in order per sensor id |
```

The aspects that most connections need a word on: latency, throughput, concurrency, ordering, delivery, idempotency, timeout, availability, limits and security. Any other aspect is allowed. The checker reads the form of the table and nothing of its content; the quality goals of a unit's `requirements.md` may link to its rows.
