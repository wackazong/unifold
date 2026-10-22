---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# A reading joins the plant its sensor stick is attached to when it is handled

## Context and Problem Statement

A reading names a sensor stick, not a plant. A sensor stick can be moved from one plant to another. Readings arrive late, sometimes days after they were taken. To which plant does a reading belong: the one the sensor stick was attached to when the reading was taken, or the one it is attached to when `plants` handles the event?

## Considered Options

- Store readings per sensor stick, keep the periods of attachment, and join at query time by the time of the reading
- Decide at handling time by the time of the reading and the periods of attachment
- Decide at handling time by the current attachment and store the plant with the reading

## Decision Outcome

Chosen option: "the current attachment at handling time", because it needs one lookup per event and no history of attachments. The moment at which a sensor stick was physically moved is known to nobody exactly, so the other options would be precise only in appearance.

### Consequences

- Good: one lookup per event, one plant per reading, no periods to maintain.
- Good: deleting a plant deletes exactly its rows.
- Bad: readings that were taken before a sensor stick was moved and are uploaded after it land in the history of the new plant. A client avoids this by uploading what it holds before it changes the attachment.
- Bad: readings that arrive while a sensor stick is attached to no plant are dropped. A client attaches first, then uploads.
- Bad: handling the same events again after a change of attachment gives a different history. A replay is therefore no exact rebuild.
