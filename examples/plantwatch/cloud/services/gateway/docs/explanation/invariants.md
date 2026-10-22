# Invariants of gateway

What is true of the entry point at every moment. These lines protect the
one promise of the unit: a provider may trust the owner it is told.

- No request reaches a provider without a verified token, and no owner id
  that came from outside is ever passed on.
- No log line contains a token or the signing key, not even shortened.
- `gateway` reads and changes no body. If a response needs another form,
  the provider changes it.
- `gateway` answers no request for a provider, for example from a cache.
  Only the two token operations are its own.
- A route is a path prefix and a need. Nothing routes by header, by owner
  or by body.
- Verification comes before every other use of a request. Rate limits are
  counted per token and therefore after it.
- An instance uses the clock of the host and keeps no clock of its own. A
  wrong clock rejects valid tokens or accepts expired ones.
