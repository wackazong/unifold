# Conventions

The stack, the folder idiom and how a unit receives what it needs. The two tables are read by `maike.py`.

## Stack

Python 3.12, pytest 8 as the test runner, `uv` for dependencies and the virtual environment, ruff for lint and format, mypy for types. The real serial port is reached through pyserial; no other library.

## Units

| Unit | Interface | Implementation | Tests |
|---|---|---|---|
| `session` | `src/serial_line/session/api.py` | `src/serial_line/session/impl.py` | `tests/session/` |
| `codec` | `src/serial_line/codec/api.py` | `src/serial_line/codec/impl.py` | `tests/codec/` |
| `transport/framing` | `src/serial_line/transport/framing/api.py` | `src/serial_line/transport/framing/impl.py` | `tests/transport/framing/` |
| `transport/serial` | `src/serial_line/transport/serial/api.py` | `src/serial_line/transport/serial/impl.py` | `tests/transport/serial/` |

## Commands

| Command | Line |
|---|---|
| `install` | `uv sync` |
| `check` | `uv run pytest -q && uv run ruff check . && uv run ruff format --check . && uv run mypy src` |
| `test-one` | `uv run pytest -q FILE` |
| `worktree` | `uv sync` |
| `run` | `uv run serial-line --port /dev/ttyUSB0` |

## Idiom

- Every part of a contract is a function or a dataclass in the interface module; `result<T, E>` becomes a return value or a raised exception class named after the variant case, as `SessionError.Timeout`.
- A unit receives what it needs as constructor arguments typed with the interface protocol of the need, so a test passes a fake.
- A value a unit keeps opaque, such as the framing buffer, is a dataclass of that unit's interface module.
