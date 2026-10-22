---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Callers authenticate with self-contained signed tokens

## Context and Problem Statement

Every request must be tied to an owner. An owner in version 1 has no e-mail address and no password; an owner comes into being when a client first starts. `gateway` shall run in several instances and shall never be the reason that an upload fails. How does a client prove for which owner it acts?

## Considered Options

- Random session tokens, looked up in a database on every request
- An external identity provider with OpenID Connect
- Self-contained tokens that `gateway` signs and verifies with a secret key

## Decision Outcome

Chosen option: "self-contained signed tokens", because verification then needs no storage and no other service, and version 1 has no account data that an identity provider could manage.

`gateway` creates an owner by issuing a token for a new random owner id. A token is valid for 365 days and is renewed by the client. The form is in
[tokens](../references/tokens.md).

### Consequences

- Good: `gateway` needs no database and no shared state. Instances are interchangeable.
- Good: a request is verified without a network call.
- Good: no personal data is needed to become an owner.
- Bad: a single token cannot be withdrawn. A stolen token works until it expires.
- Bad: a client that loses its token loses access to the owner's plants. Nothing can restore it.
- Bad: the signing key is a secret whose loss exposes every owner.
- Bad: accounts with login would need a new decision and a place to store them.
