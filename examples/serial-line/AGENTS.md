<!-- unifold:generated - do not edit; run `unifold generate` -->
# AGENTS.md: serial-line

unifold unit; run `unifold show` here. Read [README.md](README.md) first: it says what the unit is for and why it is built this way. Everything else is in `docs/`.

## Documents

| Kind | Files |
|---|---|
| Look up | [clock](docs/references/clock.md), [constants](docs/references/constants.md), [conventions](docs/references/conventions.md), [frames](docs/references/frames.md), [glossary](docs/references/glossary.md), [host](docs/references/host.md), [test-kit](docs/references/test-kit.md), [transport](docs/references/transport.md), [uart](docs/references/uart.md) |
| Understand | [decisions](docs/decisions/index.md) |

<!-- unifold:begin - generated block; run `unifold generate` to refresh -->
## unifold

This repository has a [unifold](https://unifold.md) map. A folder with a `unifold.yaml` is a unit: the file says what the unit provides and needs, and the unit above connects needs to providers. Read the map before you change an interface; keep it true after.

- `unifold show PATH`: a unit, its capabilities and needs, and who is on the other side
- `unifold capability PATH NAME`: both ends of one connection, with contracts
- `unifold check`: is the map consistent (`--fix` rewrites generated files)

| Unit | Path | Responsibility |
|---|---|---|
| codec | `codec` | Encodes a payload into the bytes of a frame and decodes a frame from bytes (planned) |
| session | `session` | Runs the host side of a session through its states and timeouts (planned) |
| transport | `transport` | Sends and receives frames over the serial line (planned) |
| framing | `transport/framing` | Cuts the byte stream from the line into frames (planned) |
| serial | `transport/serial` | Moves frames through the serial port with deadlines (planned) |
<!-- unifold:end -->
