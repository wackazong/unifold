# gateway

`gateway` is the one HTTP endpoint that clients reach. It issues and verifies tokens, limits request size and request rate, and passes each request on to whoever serves it. It keeps no data and looks into no body.

## Why

What this unit hides is the form and the verification of tokens ([0001](docs/decisions/0001-self-contained-signed-tokens.md)). Clients need one address and one way to prove for which owner they act. `gateway` exists so that this is solved once: it is the only code that understands tokens, and everything it passes a request to may trust the owner it is told. It changes when the way a client proves its owner changes, or when the public API gets a new group of paths.

It is cut as thin as possible. It routes by path prefix and does not look into bodies, so a change to a resource never needs a change here. It keeps no data, so any number of instances can run and none of them is a reason for an upload to fail. That is why tokens are self-contained and signed instead of looked up ([0001](docs/decisions/0001-self-contained-signed-tokens.md)), and why rate limits are counted in memory ([0002](docs/decisions/0002-rate-limits-are-counted-per-instance.md)).

The price of statelessness: a token cannot be withdrawn, and whoever holds the signing key can act for every owner. The key is the one secret of this unit.

What must stay true: no request reaches a provider without a verified token, and no owner id that came from outside is ever passed on.

## Read next

1. [routing](docs/references/routing.md): how a request is handled and where it goes
2. [docs/references/tokens.md](docs/references/tokens.md): form, signing and verification of tokens
3. [docs/explanation/context.md](docs/explanation/context.md): what the unit inherits
4. [Decisions](docs/decisions/index.md)
