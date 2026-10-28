# Runtime of cloud

Stories that cross several services and that no single service can tell are scenarios in `unifold.yaml`. Which services exist is in the [component diagram](../diagrams/component.md).

## An upload that leads to an alert

The scenario [upload-leads-to-alert](../diagrams/scenario-upload-leads-to-alert.md) follows one batch from the client through `gateway` and `ingest` onto the event bus, and from there into the history of `plants` and the judgement of `alerts`, up to the notification and the client's next queries.

The upload is answered before history and evaluation have seen the reading. The two branches run independently and in any order: a client sees the reading in the history within 10 seconds and an alert within 1 minute after the upload response.
