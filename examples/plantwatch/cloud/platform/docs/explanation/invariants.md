# Invariants of platform

What is true of the shared infrastructure at every moment. What a service may rely on is in the contracts of the two capabilities.

- A service relies on the two contracts without knowing the products behind them.
- The database itself enforces the isolation between schemas. A role has rights on its own schema and on no other, not even read-only and not "for a moment". A report across schemas is a capability of a service, not a grant.
- `platform` creates no table, view or function inside a service's schema.
- A topic that is not declared in this unit does not exist, in every environment. No topic is created on first use.
