---
status: proposed
date: 2026-10-27
---

# What the host does with a frame whose CRC is wrong

## Context and Problem Statement

Proto §4.3 says that a frame whose CRC does not match is invalid and that what a receiver does with it "is a matter of the implementation"; it says what the device does, not what the host does. The host may get such a frame while it waits for an ACK. The choice changes the contract `transport.receive` and the behaviour of `open` and `close`, so it is a question for the owner of the project.

## Options

- Drop the frame and keep waiting until the deadline, as the device does.
- Report `line-error` and close the session: a corrupted line is not to be trusted.

## Recommendation

Drop the frame and keep waiting: it matches the device, a single corrupted byte then costs one retry by the caller instead of a session, and the contracts already describe it this way.

## Answer

