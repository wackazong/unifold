# soil-probe

Contract of the need `soil-probe` of plantwatch: the capacitive probe in the pot. The firmware is calibrated for one type of probe, not for the single probe. Notation: the electrical properties as text.
Sources: the data sheet of the probe type, reduced to what the firmware relies on.

## Parts

### output

Kind: query

```text
supply on (2.0 V to 3.3 V), wait >= 100 ms, measure output -> share of the supply, 0.0 to 1.0
```

Pre: the supply is 2.0 V to 3.3 V and has been on for at least 100 ms; the supply is switched on only while a measurement runs.
Result: an analogue voltage between 0 V and the supply voltage that falls as the soil gets wetter. The output is proportional to the supply voltage, so the firmware measures it as a share of the supply. The output is stable within 100 ms after power-on. The probe draws at most 5 mA.
Errors: none; a probe has no way to report a fault.
Examples:

| Case | Input | Expected |
|---|---|---|
| in air | the probe is in air | the output is close to the supply voltage |
| saturated | the probe is in saturated soil | the output is well below half the supply voltage |
| supply drops | the supply drops from 3.0 V to 2.4 V in the same soil | the share of the supply is the same |

### probe

Kind: type

```text
probe { output: analogue voltage 0 V to supply, falling with moisture; supply: 2.0 V to 3.3 V, switched; current: <= 5 mA; settling: 100 ms }
```

| Property | Value |
|---|---|
| output | an analogue voltage between 0 V and the supply voltage that falls as the soil gets wetter |
| proportional | the output is proportional to the supply voltage |
| supply | 2.0 V to 3.3 V, switched on only while a measurement runs |
| current | at most 5 mA |
| settling | the output is stable within 100 ms after power-on |

## Fake

A simulated probe: a voltage source that a test sets as a share of the supply, with the settling time. Faults it can inject: output stuck at the supply voltage, as a probe in air or a broken wire shows.
