# Soil probe

The contract of the need `soil-probe`: the capacitive probe in the pot.

| Property | Value |
|---|---|
| Output | An analogue voltage between 0 V and the supply voltage that falls as the soil gets wetter |
| Proportional | The output is proportional to the supply voltage; the firmware measures it as a share of the supply |
| Supply | 2.0 V to 3.3 V, switched on only while a measurement runs |
| Current | At most 5 mA |
| Settling | The output is stable within 100 ms after power-on |

The firmware is calibrated for one type of probe, not for the single probe.

## Examples

| Case | Expected |
|---|---|
| The probe is in air | The output is close to the supply voltage |
| The probe is in saturated soil | The output is well below half the supply voltage |
| The supply drops from 3.0 V to 2.4 V in the same soil | The share of the supply is the same |
