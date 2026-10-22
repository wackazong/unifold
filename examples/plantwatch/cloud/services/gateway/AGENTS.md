<!-- unifold:generated - do not edit; run `unifold generate` -->
# AGENTS.md: gateway

unifold unit; run `unifold show` here. Read [README.md](README.md) first: it says what the unit is for and why it is built this way. Everything else is in `docs/`.

## Documents

| Kind | Files |
|---|---|
| Look up | [routing](docs/references/routing.md), [tokens](docs/references/tokens.md) |
| Understand | [context](docs/explanation/context.md), [invariants](docs/explanation/invariants.md), [decisions](docs/decisions/index.md) |

## Skills

| Skill | Description |
|---|---|
| [gateway-add-a-route](docs/skills/gateway-add-a-route/SKILL.md) | Make a new group of public paths reachable through the gateway. Use it when the public API gets a path prefix that no existing route covers. |
| [gateway-rotate-the-signing-key](docs/skills/gateway-rotate-the-signing-key/SKILL.md) | Replace the key with which the gateway signs tokens, either on schedule or because the key may have leaked. Use it once a year, and at once when a leak is suspected. |
