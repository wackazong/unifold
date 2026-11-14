# radio

Contract of `hal.radio`: a BLE peripheral with a GATT server for one central at a time, Bluetooth 4.2 on the LE 1M PHY. Transmit power is 0 dBm. The provider knows nothing about the meaning of an attribute. Notation: wit.
Sources: the radio stack of the board as `hal` absorbs it; the BLE profile of plantwatch for what the caller needs.
Binding: in-process

## Use

The caller configures the radio once at start, before advertising, then sets the advertising data and opens bonding when it needs to. While a central is connected, the caller answers every `read` and `write` event with `answer`. It sends notifications and indications only where the central has switched them on. `send` needs a connected central. Every radio event carries a tick count; the caller takes all time from these tick counts and has no other source of time.

## Qualities

| Aspect | Guarantee |
|---|---|
| ordering | events arrive in the order in which they happened, each with the tick count at which it happened |
| throughput | at least 4 notifications of up to 20 bytes per connection event |
| latency | after a disconnect, advertising resumes within 1 s; a change of the advertising data is on air with the next advertising event |
| limits | up to 16 characteristics of up to 128 bytes; an ATT MTU of 23 to 131 bytes; at least 4 bonds kept across power loss |
| security | bonding is LE Secure Connections, Just Works; a request on a characteristic that requires encryption over an unencrypted connection is answered by the provider itself with an ATT error |
| concurrency | `hal` delivers the events and alarms of all four contracts one after another, never two at the same time; whenever no event is being handled, the board sleeps, keeps counting time and keeps the radio schedule, and draws the sleep current of the board reference |

## Parts

### configure

Kind: operation

```wit
configure: func(characteristics: list<characteristic>, preferred: connection-preference, limits: connection-limits);
```

Pre: called once, at start, before advertising.
Result: the characteristics are declared, up to 16, in one or more services. The provider requests the preferred interval range and peripheral latency from the central and accepts every interval the central chooses. It closes the connection when the time without requests or the longest duration of `limits` is reached.
Errors: none.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| idle limit | a central is connected and sends no request for 30 s | `configure` with `limits` of 30 s without requests | the provider closes the connection and reports `disconnected` |

### set-advertising

Kind: operation

```wit
set-advertising: func(data: list<u8>, scan-response: list<u8>, on: bool, interval-ms: u16);
```

Pre: `data` and `scan-response` have up to 31 bytes each; `interval-ms` is 100 to 2000.
Result: the next advertising event carries the new bytes; the caller may replace them at any time. While advertising is on and no central is connected, the provider advertises connectable and scannable on all three advertising channels.
Errors: none.
Examples:

| Case | Input | Expected |
|---|---|---|
| new data | `set-advertising` with new data at an interval of 1285 ms | a scanner sees the new bytes at most 1285 ms later |

### open-bonding

Kind: operation

```wit
open-bonding: func(duration-s: u16);
```

Pre: none.
Result: the provider accepts a new bond until the duration ends. The provider never asks the central for security. When all places for bonds are taken, a new bond replaces the one used longest ago. While bonding is closed, the provider rejects pairing by a central without a bond with `Pairing Not Supported`.
Errors: none.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| a fifth central | 4 bonds are kept and bonding is open | a fifth central bonds | its bond replaces the one used longest ago |
| too late | the duration ended 10 s ago | a central without a bond starts pairing | rejected with `Pairing Not Supported` |

### send

Kind: operation

```wit
send: func(characteristic: u8, value: list<u8>, indicate: bool) -> result<_, no-room>;
```

Pre: a central is connected and has switched notifications or indications of the characteristic on.
Result: the provider takes the notification or indication.
Errors: `no-room` when the provider cannot take it now; `room-again` is reported later.
Examples:

| Case | Input | Expected |
|---|---|---|
| a burst | 6 calls of `send` in one connection event | the provider takes at least 4, answers `no-room` for the rest and later reports `room-again` |

### answer

Kind: operation

```wit
answer: func(request: u16, outcome: answer-outcome);
```

Pre: a `read` or `write` event with this request number is open.
Result: the provider sends the answer to the central: a value, success, or an ATT error code of the caller's choice.
Errors: none.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| a read | the read request 7 is open | `answer(7, value(18 bytes))` | the central receives the 18 bytes |

### identity

Kind: operation

```wit
identity: func() -> list<u8>;
```

Pre: none.
Result: an 8-byte identifier, unique per board, that never changes. The provider also uses a static random device address that never changes.
Errors: none.
Examples:

| Case | Input | Expected |
|---|---|---|
| twice | `identity()` before and after a restart | the same 8 bytes |

### radio-event

Kind: event

```wit
variant radio-event {
  connected,
  disconnected,
  mtu-changed(u16),
  read(request),
  write(request),
  subscription-changed(subscription),
  room-again,
}
```

When: a central connects or disconnects, the ATT MTU changes, the central reads or writes a characteristic, the central switches notifications or indications of a characteristic on or off, or the provider has room again after `no-room`.
Delivery: exactly once per event, in the order in which the events happened.

Every event carries the tick count at which it happened. `mtu-changed` carries the ATT MTU, 23 to 131 bytes. A `read` or `write` names the characteristic and, for a write, its bytes; the caller answers it with `answer`. `subscription-changed` names the characteristic and whether notifications or indications are now on; the provider keeps that state per characteristic and switches everything off at each new connection, also for a bonded central. A request on a characteristic that requires encryption over an unencrypted connection is answered by the provider itself, with ATT error `0x05` when the central has no bond and `0x0F` when it has one; the caller sees no event.

Examples:

| Case | Action | Emitted |
|---|---|---|
| a central without a bond writes to a protected characteristic | the write arrives over an unencrypted connection | nothing; the provider answers ATT error `0x05` |
| a bonded central writes before encryption is on | the write arrives over an unencrypted connection | nothing; the provider answers ATT error `0x0F` |
| a bonded central reconnects | the connection is made | `connected`; every subscription is off until the central switches it on |

### characteristic

Kind: type

```wit
record characteristic { uuid: list<u8>, properties: list<property>, max-length: u8, encrypted: bool }
```

| Field | Meaning |
|---|---|
| uuid | a 128-bit UUID |
| properties | read, write, notify, indicate |
| max-length | the largest length, up to 128 bytes |
| encrypted | whether the characteristic requires an encrypted connection |

## Fake

A radio in memory with a scripted central: a test connects the central, lets it read, write, subscribe and take notifications, and reads the advertising data back. Faults it can inject: `no-room` on the next send, a lost connection, a pairing attempt by a central without a bond.
