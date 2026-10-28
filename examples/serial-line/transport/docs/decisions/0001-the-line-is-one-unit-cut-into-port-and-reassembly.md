---
status: proposed
date: 2026-10-27
---

# The line is one unit, cut into the port and the reassembly

## Context and Problem Statement

The session needs payloads to travel over the line. Where does the knowledge of the port, its deadlines and the cutting of the byte stream into frames live?

## Considered Options

- One adapter unit that does everything between the session and the port
- An adapter for the port and a logic unit for the reassembly, together one composite adapter
- Reassembly inside the codec

## Decision Outcome

Chosen option: "a composite of port and reassembly", because the reassembly is a calculation that tests feed byte by byte and that a fake of the port would only obscure, while the port is the one place with side effects. The codec stays a layout: where a frame starts in a stream is a policy of the line, not of the layout.

### Consequences

- Good: the reassembly is tested without a port, with every split of a stream.
- Good: the port unit is small, and its contract tests run against the fake and the real port.
- Bad: one more unit and one more contract.
