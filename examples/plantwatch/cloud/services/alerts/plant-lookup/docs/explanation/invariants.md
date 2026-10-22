# Invariants of plant-lookup

What is true of `lookup` at every moment. These lines keep the caller free
of the network and keep a changed threshold from being missed.

- No answer is older than 60 seconds, and no failure reaches the caller as
  anything but `unavailable`.
- This unit holds no logic about readings, alerts or quantities. It passes
  thresholds on and compares nothing with them.
- A kept answer that is older than 60 seconds is never returned, not even
  as a fallback.
- `unavailable` is never kept. The next call asks again.
- A status of the registry that this unit does not know becomes
  `unavailable`, never `unattached`. A wrong `unattached` drops a reading
  from evaluation for good.
