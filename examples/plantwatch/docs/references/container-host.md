# container-host

Contract of the need `container-host` of plantwatch: what runs the containers of the server side. Nothing in plantwatch implements it. The clock of every container stays within 10 seconds of UTC. Notation: the requests to the host as text.
Sources: the deployment of `cloud`; no product is named.

## Parts

### run

Kind: command

```text
run(container image, name, volumes) -> the container runs on the private network
```

Pre: the image exists.
Result: the host runs the container and restarts one that stops. The container is on a private network in which containers find each other by name; nothing in it is reachable from outside unless published.
Errors: none that plantwatch relies on.
Examples:

| Case | Input | Expected |
|---|---|---|
| a container stops | a container of the server side stops | it runs again within a minute |
| name resolution | a container connects to the host name `sql-db` | it reaches the database container |

### volume

Kind: command

```text
volume(name, [separate storage device]) -> a volume that survives restart and replacement
```

Pre: none.
Result: a container that asks for a volume gets one that survives restart and replacement of the container. Two volumes can be placed on separate storage devices.
Errors: none that plantwatch relies on.
Examples:

| Case | Input | Expected |
|---|---|---|
| a container is replaced | a new container takes the place of the old one | its volume holds what the old one wrote |

### publish

Kind: command

```text
publish(container, port) -> the one port reachable from outside, with TLS terminated by the publisher
```

Pre: no other port is published.
Result: exactly one network port is reachable from outside the private network. Whoever publishes it terminates TLS.
Errors: none that plantwatch relies on.
Examples:

| Case | Input | Expected |
|---|---|---|
| a request from the internet | to a service other than the published one | no connection |

## Fake

A container runtime on the developer machine with a compose file of the server side: the same containers, network and volumes, without TLS. Faults it can inject: stop a container, replace a container, cut the network between two containers.
