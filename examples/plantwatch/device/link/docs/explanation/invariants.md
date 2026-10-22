# Invariants of link

What is true of the profile implementation at every moment. These lines
keep "what is delivered" with one owner and `link` free of state that could
outlive a connection.

- On `confirm`: mark first, indicate afterwards. On a failed mark, `link`
  indicates `storage-failure` and changes nothing.
- `link` holds at most one notification's worth of records in RAM. It takes
  the next reading from `reading-log` only when `radio` has room.
- `link` has no timer. Idle timeout, longest connection and the duration of
  open bonding are settings of `radio`; the tick count comes with each
  event. No counter works around this.
- The advertising data is refreshed after every new reading and every
  confirm.
