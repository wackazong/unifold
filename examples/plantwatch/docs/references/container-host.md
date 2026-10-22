# Container host

The contract of the need `container-host`: what runs the containers of the server side. Nothing in plantwatch implements it.

| Property | Guarantee |
|---|---|
| Containers | Runs every container of the server side and restarts one that stops |
| Network | A private network in which containers find each other by name. Nothing in it is reachable from outside unless published. |
| Volumes | A container that asks for a volume gets one that survives restart and replacement of the container. Two volumes can be placed on separate storage devices. |
| Publishing | Exactly one network port is reachable from outside the private network. Whoever publishes it terminates TLS. |
| Clocks | The clock of every container stays within 10 seconds of UTC |

## Examples

| Case | Expected |
|---|---|
| A container stops | It runs again within a minute |
| A container is replaced | Its volume holds what the old one wrote |
| A request from the internet to a service other than the published one | No connection |
