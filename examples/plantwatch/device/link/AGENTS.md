# AGENTS.md: link

This folder is a [youmedoc](https://youmedoc.example) unit.

## Why

Everything that knows the profile is in this unit: UUIDs, byte layouts, op
codes, the state of a running procedure. A change of the profile then
changes one unit, and measuring and storing never see a GATT attribute.

link owns no data. It reads stored readings where they are kept and has
them marked there. So there is one owner of "what is delivered", and a
connection that breaks leaves nothing behind in link that could disagree
with it. The only state link has is the state of the current connection,
and that is meant to vanish with the connection.

The price is that link depends on four providers and is mostly a state
machine between them. Its correctness is its agreement with a text it does
not own.

What must stay true: a fetch changes nothing; a confirm result goes out
only after the mark is durable; and no part outside link builds or parses
a record of the profile.

## Read next

1. [README.md](README.md): what a central can rely on, and what link needs
2. [doc/context.md](doc/context.md): the decisions above that fix interval, timeouts and versions
3. [doc/diagrams/context.md](doc/diagrams/context.md): the unit in its surroundings
4. [doc/decisions/index.md](doc/decisions/index.md): serving a fetch without a buffer

## Rules for work here

- The definition behind `link-profile` wins. If the code disagrees with
  it, the code is wrong. If the definition is unclear, do not settle the
  question here; the definition is not owned by this unit
  ([context](doc/context.md)).
- On `confirm`: mark first, indicate afterwards. On a failed mark,
  indicate `storage-failure` and change nothing.
- Hold at most one notification's worth of records in RAM. Take the next
  reading from `reading-log` only when `radio` has room.
- link has no timer. Idle timeout, longest connection and the duration of
  open bonding are settings of `radio`; the tick count comes with each
  event. Do not work around this with a counter.
- Refresh the advertising data after every new reading and every confirm.
- Bonded centrals remember attribute handles. Add a characteristic at the
  end of the service, never in the middle, and never reorder.
- Never compute a count from two sequence numbers. Ask `reading-log`.
