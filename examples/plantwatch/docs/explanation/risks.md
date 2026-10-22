# Risks of plantwatch

Risks and known limits of the design as it stands, each with what would
remove it. Planned work is not listed here.

## Risks

- **Readings are lost when the phone stays away too long.** A sensor stick
  keeps at least 30 days of readings and then overwrites the oldest
  undelivered one
  ([product parameters](../references/product-parameters.md)). An owner who
  is away longer loses the oldest readings before they reach the phone.
  Accepted knowingly: recent state matters more than old history. Removed
  by: a larger store on the stick, at the cost of flash and energy.
- **An upload cannot be proven to come from the owner of the sensor
  stick.** The sensor stick holds no secret, so the server side accepts
  readings under any sensor id from any client with a valid token
  ([0001](../decisions/0001-the-phone-relays-between-sensor-and-server.md)).
  Removed by: a secret on the stick, which the energy budget and the
  pairing procedure would have to carry.
- **Every decision is still proposed.** No person has accepted any decision
  of this design, so every unit stands on choices that can still move.
  Removed by: a review that accepts or rejects each decision.
- **A dead cell is noticed late.** A sensor stick that has gone silent
  produces no reading and therefore no alert; the design has no alert about
  missing data. Removed by: a rule on the server side that judges the age
  of the last reading, which would need a decision above the server side.

## What version 1 leaves out

- **Firmware updates over the air.** A sensor stick is updated by hand.
  Removed by: an update procedure in the radio protocol and a bootloader on
  the stick.
- **More than one owner per plant.** Removed by: sharing in the model of
  owners on the server side and in the app.
- **A web client.** The public API of the server side would allow one.
