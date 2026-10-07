---
status: proposed
date: 2026-10-06
---
# The plant list is home and alerts have no screen of their own

## Context and Problem Statement

The screens show plants, readings, alerts and settings. The owner comes
with one question most of the time: which plant needs me? Often they come
through a notification about one plant. How are the screens arranged, and
where do alerts appear?

## Decision Drivers

- The answer to "which plant needs me" is visible without a tap
- An alert is never seen apart from the plant and the reading behind it
- Few screens, because every screen needs all states and two languages

## Considered Options

- A tab bar with "Plants", "Alerts" and "Settings"
- A home screen that lists open alerts, with the plants one level below
- One list of plants as the home screen; open alerts are shown on the
  plants, which are sorted with alerts first; earlier alerts are on the
  plant's own screen

## Decision Outcome

Chosen option: "one list of plants, alerts shown on the plants", because an
alert is a state of a plant and not a thing of its own for the owner, and
because one list answers the main question for the owner with one plant
and for the owner with fifty.

The settings are reached from the list and are not a peer of it. A tap on
a notification opens the plant directly; "back" leads to the list.

The screens and the ways between them are in
[app-ui.md](../references/app-ui.md).

### Consequences

- Good: no screen can show an alert without its plant.
- Good: with no open alert, the home screen is simply the owner's plants,
  not an empty alert list.
- Good: one screen fewer to build, translate and keep accessible.
- Bad: there is no place that lists all alerts of the past across plants.
  An owner who wants to know "what happened last week" opens each plant.
- Bad: the order of the list changes when an alert opens or closes, so a
  plant is not always at the same position.
- Bad: with many open alerts the list is long before the first plant
  without one appears.
