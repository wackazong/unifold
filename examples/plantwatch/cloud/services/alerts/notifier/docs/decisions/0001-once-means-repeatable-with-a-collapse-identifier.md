---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# "Exactly once" means repeatable sending with a collapse identifier

## Context and Problem Statement

The port `notification` promises that the owner is told about an opened alert exactly once. Everything around it delivers at least once: `notify` can be called again after a crash of its caller, and a request to the push service can succeed although its answer is lost. `notifier` has no storage. How can "once" hold on top of "at least once"?

## Considered Options

- At most once: the caller marks the alert as notified before it calls, and never calls twice
- At least once, and accept that the owner sometimes gets two notifications
- At least once, with a collapse identifier that is the same for every attempt, so that the push service and the phone merge repeats
- A log of sent notifications in a store of its own

## Decision Outcome

Chosen option: "at least once with a collapse identifier", because a missing notification breaks the promise of the product, a doubled one annoys, and the collapse identifier removes nearly all doubles without any storage.

The collapse identifier is the alert id. Everything else in the request is derived from the alert alone, so two attempts are equal. The caller stops calling once it has stored `sent`.

### Consequences

- Good: no notification is lost because of a crash or a lost answer.
- Good: `notifier` stays without state.
- Good: an owner with several phones gets the notification on each, once.
- Bad: "once" is as good as the push service's handling of the collapse identifier. A repeat that arrives after the owner has dismissed the first one is shown again.
- Bad: the need `push` becomes narrower: a provider without a collapse identifier does not fit.
- Bad: no part of the message can vary between attempts, which rules out texts such as "10 minutes ago".

## Pros and Cons of the Options

### At most once

- Good: never two notifications.
- Bad: a crash between marking and sending loses the notification silently.

### A log of sent notifications

- Good: the caller is free of the bookkeeping.
- Bad: writing the log and sending are again two steps that can be torn apart. The log moves the problem and adds a store.
