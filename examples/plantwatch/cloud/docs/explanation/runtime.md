# Runtime of cloud

Stories that cross several services and that no single service can tell are scenarios in `unifold.yaml`.

## An upload that leads to an alert

The scenario `upload-leads-to-alert` follows a threshold that a client sets and then one batch from the client through `gateway` and `ingest` onto the event bus, and from there into the history of `plants` and the judgement of `alerts`, up to the notification and the client's next queries. What happens inside `alerts` is its own scenario `handle-a-reading`, which this one includes.

The upload is answered before history and evaluation have seen the reading. The two branches run independently and in any order: a client sees the reading in the history within 10 seconds and an alert within 1 minute after the upload response.

## A start after a stop

The scenario `the-server-side-starts-again` follows the services after the container host has started them again: `ingest` reads its accepted ranges, `plants` and `alerts` subscribe again, and the event bus delivers what a service had not confirmed. Handling an event a second time changes nothing, so a stop at any moment loses no reading and doubles none.
