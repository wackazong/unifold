---
name: gateway-add-a-route
description: Make a new group of public paths reachable through the gateway. Use it when the public API gets a path prefix that no existing route covers.
---

# Add a route

A route connects a path prefix of the public API to a need of `gateway`. A new operation below an existing prefix needs no change here.

## Steps

1. **Check that a route is missing.** Compare the new paths with the table of routes in [public API](../../references/routing.md). If an existing prefix covers them, stop: nothing changes in this unit.
2. **Check the contract.** The new paths must be part of the public API that this unit inherits ([context](../../explanation/context.md)). If they are not there yet, the change starts above this unit, not here.
3. **Declare the need**, if the paths are served by something `gateway` does not call yet. Add a need of kind `http` to the manifest, [unifold.yaml](../../../unifold.yaml), named after what is served, and describe the expectation in the `## Needs` section. The need is wired outside this unit.
4. **Add the route** to the table in [public API](../../references/routing.md): the prefix and the need. The prefix is a complete path segment below `/v1`.
5. **Cite the new prefix** in the item on the public API in
   [context](../../explanation/context.md).
6. **Add the route to the code**, as a prefix and a target, with a test for each of the checks below.

## Checks

- A request to the new prefix without token gets `401` and does not reach the provider.
- A request with a valid token reaches the provider with `X-Owner-Id` set and without `Authorization`.
- A request that carries its own `X-Owner-Id` reaches the provider with the owner id of the token, not the one it sent.
- A provider that is down leads to `503` `unavailable` after three tries.
- No existing route changed: prefixes do not overlap.

## Reference

- [public API as served by gateway](../../references/routing.md):
  routes, order of handling, what is passed on
- [context](../../explanation/context.md): the public API and the rules for calls between services
