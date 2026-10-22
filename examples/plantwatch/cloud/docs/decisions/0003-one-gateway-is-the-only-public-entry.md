---
status: proposed
date: 2026-10-06
---
# One gateway is the only public entry

## Context and Problem Statement

A client talks to several services: one accepts uploads, one answers
questions about plants, one about alerts. Each request must be tied to an
owner. Either every service is reachable from outside and authenticates by
itself, or one service stands in front of the others.

## Considered Options

- Every service is public and verifies tokens itself
- A general-purpose reverse proxy routes; every service verifies tokens
- One service of our own, [gateway](../../services/gateway/README.md), is
  the only public entry; it authenticates and routes, and the services
  behind it trust the owner id it passes on

## Decision Outcome

Chosen option: "one gateway that authenticates", because token handling
then exists once, the client sees one host and one contract, and the other
services have no public surface to protect.

The gateway does not change request or response bodies. What a service
answers is what the client receives. The public contract is therefore the
sum of what the services behind the gateway serve; it is written down once,
in the [public API](../references/public-api/index.md). How the gateway
passes on the caller is defined in
[service calls](../references/service-calls.md).

### Consequences

- Good: one place for authentication, rate limits and request size limits.
- Good: services can be split or merged without a change for clients.
- Bad: the services trust the private network. A caller inside it can act
  for any owner.
- Bad: every request passes one more hop, and the gateway must run in more
  than one instance to be no single point of failure.
- Bad: because bodies pass unchanged, a service cannot change a public
  resource without changing the public contract.
