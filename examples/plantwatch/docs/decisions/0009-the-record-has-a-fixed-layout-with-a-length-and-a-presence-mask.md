---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# The record has a fixed layout with a length and a presence mask

## Context and Problem Statement

A reading crosses the radio link in binary form. The link carries 20 bytes of payload per packet unless both sides negotiate more. A sensor stick has little memory and computing power. Quantities will be added later, and a part built for an earlier version must keep working with a part built for a later one. Which encoding does the record use?

## Decision Drivers

- One reading fits into one packet at the default ATT MTU.
- A receiver built for version 1.0 reads a record of a later 1.x version.
- Encoding and decoding need no library and no memory allocation.
- "Not measured" is distinguishable from every valid value.

## Considered Options

- JSON, the same text as in the upload form
- A self-describing binary format such as CBOR, or tag-length-value fields
- A fixed layout without length: fields at fixed offsets, a special number for "not measured"
- A fixed layout with a leading length byte and a presence bit mask

## Decision Outcome

Chosen option: "a fixed layout with a leading length byte and a presence bit mask", because it is the only option that meets all four drivers.

A new quantity gets the next mask bit and bytes after the last field. An old receiver skips those bytes by means of the length. A new receiver treats bytes beyond the length of an old record as absent.

### Consequences

- Good: a version 1.0 record has 19 bytes and fits into one notification.
- Good: a sender fills a struct, a receiver reads at fixed offsets.
- Good: no value is misused as a marker; the full range of every field stays available.
- Bad: an absent quantity still occupies its bytes.
- Bad: the order of fields is fixed for the whole major version. A quantity cannot be removed, only left absent.
- Bad: the mask has 8 bits. Major version 1 can carry at most 8 quantities.
- Bad: the JSON form and the binary form are two encodings to keep in step.

## Pros and Cons of the Options

### JSON

- Good: one form everywhere.
- Bad: a reading has about 200 bytes, that is ten packets.
- Bad: a sensor stick needs a JSON writer.

### Self-describing binary format

- Good: fields can be added and left out freely.
- Bad: every field pays one or two bytes for its tag; a reading no longer fits into 20 bytes.
- Bad: a sensor stick needs an encoder, a receiver a decoder.

### Fixed layout without length

- Good: smallest record.
- Bad: no field can be added without a new major version.
- Bad: one number per field is lost to "not measured".

## More Information

The layout is defined in the
[reading schema](../references/reading-schema.md).
