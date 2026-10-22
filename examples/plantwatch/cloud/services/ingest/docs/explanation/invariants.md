# Invariants of ingest

What is true of the upload path at every moment. These lines keep the
moment of an upload as hard to fail as possible.

- The upload path depends on the event bus and on nothing else: no
  database, no cache, no call to another service.
- A response is sent only after the event bus has acknowledged every event
  of the batch and the new accepted range. An answer before that can lose
  readings.
- An event is published first, the accepted range recorded second. The
  other order turns a failure into a lost reading instead of a repeated
  event.
- No reading is changed. The `reading` field of an event is what was
  uploaded, including fields that `ingest` does not know.
- A rejection is final for the client, who will not send the reading
  again. A reading is therefore rejected only for a reason that can never
  become valid; everything that might work later answers `503`.
