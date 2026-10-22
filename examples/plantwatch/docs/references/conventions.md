# Conventions

Rules that hold in every unit of plantwatch. The terms are defined in the
[glossary](glossary.md).

## Measured quantities

| Quantity | Unit | Range | Resolution |
|---|---|---|---|
| Soil moisture | percent of the calibrated range | 0 to 100 | 0.1 |
| Light | lux | 0 to 100 000 | 1 |
| Temperature | degrees Celsius | -20 to 60 | 0.1 |

A value outside its range is invalid and is rejected by the first receiver.
A quantity that could not be measured is absent, not zero.

## Identifiers

| Thing | Form |
|---|---|
| Sensor id | 8 bytes, written as 16 lower-case hex digits |
| Sequence number | Unsigned 32-bit integer |
| Plant, owner, alert | UUID in lower-case text form |

A reading is identified by sensor id and sequence number together.

## Time

- Outside the sensor stick, every time is UTC.
- In APIs and stored documents a time is an RFC 3339 string with the suffix
  `Z` and whole seconds.
- A time that was estimated carries a flag saying so.

## Delivery

- Every transfer of readings or events may deliver an item more than once.
- Every receiver accepts an item it already has and reports success.
- A sender deletes an item only after the receiver has confirmed it.

## HTTP ports

- Request and response bodies are JSON in UTF-8.
- Field names are lower-case with underscores.
- An error response has a JSON body with the fields `code` and `message`.
- A request that repeats an earlier successful request succeeds again.

## Changing a shared definition

- The radio protocol and the reading format are changed in the unit that
  defines them, before any part that uses them changes.
- A change that an older counterpart cannot ignore needs a new major
  version and a decision of plantwatch.

## Names

- Unit and capability names are lower-case with hyphens.
- A need is named after what is needed, never after who provides it.

## Working in this repository

- The project is in its design phase. Nobody writes product code for a unit
  before a person has accepted the decisions that unit depends on.
- A change to the radio protocol or to the reading format follows
  [Changing a shared definition](#changing-a-shared-definition).
- Every file uses the terms of the [glossary](glossary.md) unchanged. In
  particular, a "reading" is one measurement set, never a single value.
- Every change ends with `unifold check --fix`, then `unifold check`.
