# Behaviour and host requirements of the emulator

What the emulator needs from the machine it runs on, and the behaviour of the simulated sensor stick.

| Topic | Fact |
|---|---|
| Host | A Bluetooth LE controller that can act as a peripheral; without it the radio face does not exist |
| Radio | The emulator sends nothing the profile does not name |
| Sampling interval | As the scenario states, 300 s to 3600 s; 900 s by default |
| Readings | One reading at every simulated start, then one per interval, with the values of the scenario rounded to the resolution of each quantity |
| Sequence numbers | They rise strictly across a simulated restart, and are consecutive unless the scenario asks for a gap |
| Boot counter | It rises by one at every simulated restart |
| Time | The seconds follow simulated time exactly |
| Retention | 2 880 unconfirmed readings are kept through a simulated restart |
| Full memory | The oldest reading is discarded and the overflow is reported |
| Advertising | Every 250 ms while no central is connected and the stick is in range |
| Bonding | Open during the first 300 s of simulated time after every start; 4 bonds are kept through a restart |
| Always-open bonding | A scenario can ask for bonding that is always open, which departs from the profile in this one point |
