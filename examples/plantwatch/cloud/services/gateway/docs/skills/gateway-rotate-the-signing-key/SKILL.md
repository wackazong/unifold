---
name: gateway-rotate-the-signing-key
description: Replace the key with which the gateway signs tokens, either on schedule or because the key may have leaked. Use it once a year, and at once when a leak is suspected.
---

# Rotate the signing key

The result is a new current key. On a scheduled rotation old tokens stay valid. After a leak they stop working, and every client must become a new owner or be given a new token by other means.

## Steps: scheduled rotation

1. Generate 32 random bytes with a cryptographic random source. Choose a key id that is not in use, for example the date.
2. Add the key to the secret store as an accepted key, not yet as the current one. Deploy all instances.
3. Check that every instance has the new key (below). Only then make it the current key and deploy again. In between, no instance issues a token that another instance cannot verify.
4. Note the date. The previous key can be removed 365 days later, when the last token signed with it has expired.

## Steps: after a leak

1. Do steps 1 to 3 of the scheduled rotation without delay.
2. Remove the leaked key from the accepted keys and deploy. Every token signed with it now gets `401`.
3. Tell a human. Clients with such a token have lost access to their owner; restoring it is outside this unit.

## Checks

- A token issued by one instance is accepted by every other instance.
- A token signed with the previous key is still accepted after a scheduled rotation, and rejected after a leak.
- The key appears in no log, no file of the repository and no error message.

## Reference

- [tokens](../../references/tokens.md): keys, key ids, verification
