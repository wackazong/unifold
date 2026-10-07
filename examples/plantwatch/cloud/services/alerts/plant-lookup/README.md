# plant-lookup

`plant-lookup` is an adapter. It answers one question as a plain function
call: to which plant is this sensor stick attached, who owns that plant and
what are its thresholds. Behind the function it asks the registry of plants
over HTTP, repeats a call that failed and keeps an answer for 60 seconds.
Its caller needs to know nothing about HTTP, time limits or network errors.

## Provides

### `thresholds`

One function, `lookup(sensor_id)`, with three possible answers:

| Answer | Content |
|---|---|
| `attached` | The plant with plant id, owner id and name, and its thresholds: per quantity a `min`, a `max` or both |
| `unattached` | Nothing. The sensor stick is attached to no plant. |
| `unavailable` | Nothing. The registry gave no usable answer in time. |

A caller can rely on this:

- **Three answers and nothing else.** `lookup` raises no error. Every
  failure of the network or of the registry becomes `unavailable`.
- **At most 60 seconds old.** An `attached` or `unattached` answer shows
  the registry as it was at most 60 seconds before the call.
- **Never older.** When the registry cannot be reached and no answer of
  that age is kept, the answer is `unavailable`, also when an older one is
  known.
- **Bounded time.** `lookup` returns within 17 seconds, and within 1 ms
  when it answers from memory.
- **Few requests.** While the registry answers, `plant-lookup` sends at
  most one request per sensor stick in 60 seconds.
- **Nothing is interpreted.** Thresholds are passed on as the registry
  gives them, for every quantity name.

Limits:

- Kept answers live in memory. After a restart the first call for a sensor
  stick asks the registry.
- Every instance keeps its own answers. Two instances can give answers of
  different age, both at most 60 seconds old.
- A threshold that was changed, and a sensor stick that was moved to
  another plant, can show up to 60 seconds late.

Example:

```text
lookup("00a1b2c3d4e5f607")
  -> attached, plant {0b6f6f0e-…, owner 5b0e2d0a-…, "Monstera in the hall"},
     thresholds {soil_moisture: {min: 30.0}}
lookup("ffffffffffffffff")
  -> unattached
```

Contract: [thresholds lookup](doc/references/thresholds.md).

## Needs

### `plants-api`

An HTTP service inside the private network with one operation that
`plant-lookup` uses: given a sensor id, it returns the plant to which the
sensor stick is attached, with plant id, owner id, name and thresholds.
`plant-lookup` calls the operation in the form that `plants-api` defines
and expects that

- the operation needs no owner and can be repeated,
- an answer shows the current state of the registry,
- a sensor stick that is attached to no plant gets an answer of its own
  that cannot be mistaken for a failure,
- an answer arrives within 5 seconds, or the status `503` when the
  provider cannot give one.

## Out of scope

- Judging a reading, or deciding what happens to a reading while the
  answer is `unavailable`.
- Any other operation of the registry. `plant-lookup` changes nothing
  there.
- Keeping answers across a restart, or sharing them between instances.
- Telling its caller that a plant has changed. It answers when asked.

## More

- [AGENTS.md](AGENTS.md): why the lookup is a unit of its own
- [doc/context.md](doc/context.md): what the unit inherits
- [Context diagram](doc/diagrams/context.md)
- [Decisions](doc/decisions/index.md)
- References: [thresholds lookup](doc/references/thresholds.md)
