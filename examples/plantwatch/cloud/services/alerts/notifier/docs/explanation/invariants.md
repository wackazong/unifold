# Invariants of notifier

What is true of `notify` at every moment. These lines make a second call
for the same alert harmless.

- `notify` is safe to call again, and `sent` is never reported on a guess.
- The collapse identifier is the alert id and nothing else: no attempt
  number, no time, nothing that differs between two calls for the same
  alert.
- Nothing in the message differs between two calls for the same alert. No
  "sent at", no counters.
- `sent` is never returned after a timeout, even if the request probably
  arrived.
- `notify` does not retry. One call is one attempt; the caller owns the
  schedule.
