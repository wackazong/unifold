# Record a decision

1. Choose the lowest unit whose insides the decision fully covers. A decision about how two siblings talk belongs to their parent.
2. Write `docs/decisions/NNNN-short-title.md` with the next free number, from [decision.template.md](../assets/decision.template.md).
3. Keep `status: proposed`; a person accepts. Where a source settles the matter, write it from [decision-derived.template.md](../assets/decision-derived.template.md) instead. The rules of decisions: <https://unifold.md/decision-records>.
4. To change an accepted decision, write a new one and set the old one to `superseded by NNNN`.
5. Rewrite every document that the decision changes to the new state, in the same change. In a unit below that depends on it, add an item to `docs/explanation/context.md` from [context.template.md](../assets/explanation/context.template.md).
6. [Finish](../SKILL.md#4-finish).
