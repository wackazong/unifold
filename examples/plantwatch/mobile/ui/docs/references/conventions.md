# Conventions of ui

How work on the screens is done. What must hold at every moment is in [invariants.md](../explanation/invariants.md).

- Every text exists in English and German. A text that is built from parts, such as "2 hours ago", is built by the platform's formatting, not by joining words.
- Times arrive in UTC. Convert to the phone's time zone at the last moment, for display only.
- Describe a screen in [screens](screens.md) before building it, with all its states. A screen with an undescribed state is not finished.
