# container-host

Contract of the need `container-host` of plantwatch: what runs the containers of the server side. Nothing in plantwatch implements it. Notation: the requests to the host as text.
Sources: the deployment of `cloud`; no product is named.
Binding: cli
Version: 1

## Use

The server side asks the host for its volumes, runs each container with its name and its volumes, and publishes at most one port. It asks for three volumes, one for the event bus, one for the database and one for database backups, and places the backup volume on other storage than the database volume; `platform` publishes no port. Apart from that one port, the host has no state that limits the calls: `run` and `volume` may be called at any time.

## Qualities

| Aspect | Guarantee |
|---|---|
| clock | the clock of every container stays within 10 seconds of UTC |
| availability | a container that stops runs again within a minute |
| durability | a volume survives restart and replacement of its container; two volumes can be placed on separate storage devices |
| security | the containers are on a private network in which they find each other by name; nothing in it is reachable from outside except the one published port, whose publisher terminates TLS |

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

| Case | Given | Input | Expected |
|---|---|---|---|
| a container stops | | `run(image, "ingest", volumes)` | the container runs; when it stops, it runs again within a minute |
| name resolution | the database container runs under the name `sql-db` | `run` of a container that connects to the host name `sql-db` | it reaches the database container |

### volume

Kind: command

```text
volume(name, [separate storage device]) -> a volume that survives restart and replacement
```

Pre: none.
Result: a container that asks for a volume gets one that survives restart and replacement of the container. Two volumes can be placed on separate storage devices.
Errors: none that plantwatch relies on.
Examples:

| Case | Given | Input | Expected |
|---|---|---|---|
| a container is replaced | the old container wrote to the volume `db-data` | `run` of a new container that takes the place of the old one, with `db-data` | its volume holds what the old one wrote |

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
| one port | `publish(gateway, 443)` | the port is reachable from the internet with TLS terminated by the publisher; a request from the internet to any other service gets no connection |

## Fake

A container runtime on the developer machine with a compose file of the server side: the same containers, network and volumes, without TLS. Faults it can inject: stop a container, replace a container, cut the network between two containers.
