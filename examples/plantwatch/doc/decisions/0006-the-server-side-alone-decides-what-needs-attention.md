---
status: proposed
date: 2026-10-06
---
# The server side alone decides whether a plant needs attention

## Context and Problem Statement

A reading can be compared with the thresholds of its plant in several places:
on the sensor stick, in the phone app when it fetches, or on the server. If
more than one place judges, an owner can see a plant marked dry in the app
without an alert, or get a notification for a plant the app shows as fine.

## Considered Options

- The phone app judges readings when it fetches them and shows the result
  at once
- The server side judges every reading; every other part shows or carries
  what the server side decided

## Decision Outcome

Chosen option: "the server side judges", because alerts must also open when
nobody opens the app, and one place of judgement gives one answer.

### Consequences

- Good: the app, a notification and the history never disagree.
- Good: the rules of judgement can change without an app release.
- Bad: a freshly fetched reading shows in the app without a verdict until
  the phone has had a network connection.
- Bad: the thresholds an owner edits offline take effect only after they
  have reached the server.
