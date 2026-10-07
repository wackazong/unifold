# AGENTS.md: gateway

This folder is a [unifold](https://unifold.md) unit. The standard and
its skills `read-docs`, `write-docs` and `check-docs` are in the project
root, the nearest folder above whose manifest contains `unifold`. From
there, `python3 doc/skills/check-docs/scripts/unifold.py show cloud/services/gateway`
prints this unit with its neighbours.

## Why

Clients need one address and one way to prove for which owner they act.
`gateway` exists so that this is solved once: it is the only code that
understands tokens, and everything it passes a request to may trust the
owner it is told. It changes when the way a client proves its owner
changes, or when the public API gets a new group of paths.

It is cut as thin as possible. It routes by path prefix and does not look
into bodies, so a change to a resource never needs a change here. It keeps
no data, so any number of instances can run and none of them is a reason
for an upload to fail. That is why tokens
are self-contained and signed instead of looked up
([0001](doc/decisions/0001-self-contained-signed-tokens.md)), and why rate
limits are counted in memory
([0002](doc/decisions/0002-rate-limits-are-counted-per-instance.md)).

The price of statelessness: a token cannot be withdrawn, and whoever holds
the signing key can act for every owner. The key is the one secret of this
unit.

What must stay true: no request reaches a provider without a verified
token, and no owner id that came from outside is ever passed on.

## Read next

1. [README.md](README.md): what the unit provides and needs
2. [doc/context.md](doc/context.md): the public API and the rules for
   calls that it inherits
3. [doc/diagrams/context.md](doc/diagrams/context.md): the unit in its
   surroundings
4. [doc/decisions/index.md](doc/decisions/index.md): decisions
5. [doc/references/public-api.md](doc/references/public-api.md): how a
   request is handled and where it goes
6. [doc/references/tokens.md](doc/references/tokens.md): form, signing and
   verification of tokens

## Skills

| Skill | Use it when |
|---|---|
| [gateway-add-a-route](doc/skills/gateway-add-a-route/SKILL.md) | The public API gets a new group of paths |
| [gateway-rotate-the-signing-key](doc/skills/gateway-rotate-the-signing-key/SKILL.md) | The signing key is due for rotation, or may have leaked |

## Rules for work here

- Never log a token or the signing key, not even shortened.
- Never add code that reads or changes a body. If a response needs
  another form, the provider changes it.
- Never answer a request for a provider, for example from a cache.
- A route is a path prefix and a need. Do not route by header, by owner or
  by body.
- Verification comes before every other use of a request. Rate limits are
  counted per token, so they come after it.
- The clock matters: a wrong clock rejects valid tokens or accepts expired
  ones. Instances rely on the host for synchronised time.
