# soil-probe

Contract of the need `soil-probe` of plantwatch: the capacitive probe in the pot. The firmware is calibrated for one type of probe, not for the single probe. Notation: the electrical properties as text.
Sources: the data sheet of the probe type, reduced to what the firmware relies on.
Binding: analogue
Version: 1

## Use

The firmware switches the supply on, waits at least 100 ms, measures the output as a share of the supply and switches the supply off. The probe has no state beyond its supply: a measurement may start whenever the supply has been on for 100 ms.

## Qualities

| Aspect | Guarantee |
|---|---|
| settling | the output is stable within 100 ms after power-on |
| power | at most 5 mA while the supply is on |
| supply | 2.0 V to 3.3 V, switched on only while a measurement runs |
| proportionality | the output is proportional to the supply voltage, so a share of the supply does not depend on the state of the cell |

## Parts

### output

Kind: query

```text
supply on (2.0 V to 3.3 V), wait >= 100 ms, measure output -> share of the supply, 0.0 to 1.0
```

Pre: the supply is 2.0 V to 3.3 V and has been on for at least 100 ms; the supply is switched on only while a measurement runs.
Result: an analogue voltage between 0 V and the supply voltage that falls as the soil gets wetter. The output is proportional to the supply voltage, so the firmware measures it as a share of the supply.
Errors: none; a probe has no way to report a fault.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| in air | the probe is in air | the output is measured | close to the supply voltage |
| saturated | the probe is in saturated soil | the output is measured | well below half the supply voltage |
| supply drops | the supply drops from 3.0 V to 2.4 V in the same soil | the output is measured as a share of the supply | the same share as at 3.0 V |

## Fake

A simulated probe: a voltage source that a test sets as a share of the supply, with the settling time. Faults it can inject: output stuck at the supply voltage, as a probe in air or a broken wire shows.
