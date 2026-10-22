# Tokens

The form of the tokens that `gateway` issues and verifies. For a client a token is an opaque string; nothing here is part of the public contract. The reasons are in [0001](../decisions/0001-self-contained-signed-tokens.md).

## Form

A token is a JSON Web Token ([RFC 7519](https://www.rfc-editor.org/rfc/rfc7519)) with a signature of the kind HS256 (HMAC with SHA-256).

| Place | Field | Content |
|---|---|---|
| Header | `alg` | Always `HS256` |
| Header | `kid` | The id of the signing key |
| Payload | `sub` | The owner id |
| Payload | `iat` | Time of issue, seconds since 1970 |
| Payload | `exp` | Time of expiry: `iat` plus 365 days |

A token carries nothing else: no name, no rights, no device.

## Signing keys

| Item | Value |
|---|---|
| Key | 32 random bytes |
| Key id | A short text chosen at rotation, for example the date |
| Source | The configuration of the instance, from the deployment's secret store |
| Number of keys | One current key, and any number of earlier keys that are still accepted |

- A new token is always signed with the current key.
- All instances have the same keys.
- An earlier key stays configured until every token signed with it has expired, that is 365 days after its last use for signing, unless it is withdrawn because it leaked.

## Verification

A token is valid when all of this holds:

| Check | Detail |
|---|---|
| Form | Three parts, header and payload are JSON |
| Algorithm | `alg` is exactly `HS256`. Any other value, also `none`, is rejected. |
| Key | `kid` names a configured key |
| Signature | Matches, compared in constant time |
| Expiry | `exp` is later than now. A clock difference of 60 seconds is tolerated. |
| Issue | `iat` is not later than now plus 60 seconds |
| Owner | `sub` is a UUID in lower-case text form |

Every failure leads to the same answer, `401` `unauthenticated`, with a `message` that does not say which check failed.

Examples, with one configured key `2026-10`:

| Token | Result |
|---|---|
| Signed with `2026-10`, `exp` in 300 days | Valid |
| The same, `exp` 30 seconds ago | Valid: within the tolerated 60 seconds |
| The same, `exp` 61 seconds ago | `401` |
| `alg` is `none`, no signature | `401` |
| `kid` is `2025-10`, a key that is not configured | `401` |
| One character of the payload changed | `401`: the signature does not match |
| `sub` is `not-a-uuid`, signature correct | `401` |

## What follows from the form

- Verification needs no lookup. An instance verifies a token with its configuration alone.
- No list of owners or of issued tokens exists.
- A single token cannot be withdrawn. Withdrawing a key withdraws every token signed with it.
- Whoever knows a key that is still accepted can make a valid token for any owner id.
