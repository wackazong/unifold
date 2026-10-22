---
status: accepted
date: 2026-10-22
decision-makers: ["Alexander Walter <alexander@wackazong.com>"]
---

# Speak real BLE through a Bluetooth controller of the host

## Context and Problem Statement

The program stands in for a sensor stick. Whatever talks to a sensor stick shall talk to the program without being changed or configured for it. A sensor stick is reached over BLE. Over which transport is the program reached?

## Considered Options

- A substitute transport, for example the GATT operations as messages over a TCP socket
- Real BLE: the program registers a GATT server and advertises through a Bluetooth controller of the host

## Decision Outcome

Chosen option: "real BLE", because only then a central uses the same code path for a simulated and a real sensor stick, down to scanning, bonding and MTU exchange.

A virtual controller counts as a controller. It gives real BLE procedures on machines without a radio.

### Consequences

- Good: a central needs no special mode. Any central can connect.
- Good: scanning, bonding, encryption and MTU exchange are exercised.
- Bad: the host needs a controller with the peripheral role and an operating system that lets a program use it. Setup differs per operating system.
- Bad: one controller carries one simulated sensor stick. Several sensor sticks need several controllers.
- Bad: radio timing is real time and cannot be sped up with simulated time.
