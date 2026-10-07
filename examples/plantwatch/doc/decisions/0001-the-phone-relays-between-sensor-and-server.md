---
status: proposed
date: 2026-10-06
---
# The phone relays between sensor stick and server

## Context and Problem Statement

Readings are taken in a flower pot and are needed on a server that can raise
alerts when nobody looks at the app. The sensor stick is powered by a coin
cell and shall run for a year. How do readings get from the pot to the
server?

## Considered Options

- The sensor stick connects to the home Wi-Fi and uploads by itself
- A mains-powered hub in the home collects readings over BLE and uploads them
- The phone app collects readings over BLE and uploads them

## Decision Outcome

Chosen option: "the phone app relays", because it needs no extra hardware and
no network credentials on the sensor stick, and BLE is the only radio that
fits the energy budget.

### Consequences

- Good: the sensor stick stays simple and cheap, and holds no secrets.
- Good: setup is pairing with the phone and nothing else.
- Bad: readings reach the server only when a paired phone has been near.
  Alerts can be late by as long as the phone was away.
- Bad: the sensor stick must keep readings until a phone has taken them.
- Bad: the phone app must fetch in the background, which mobile operating
  systems restrict.
