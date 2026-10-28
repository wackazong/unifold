# serial-line

A program that opens a session to a device over a serial line, sends it data and closes the session, following the Serial Session Protocol. It is the small design example of unifold: three units, one of them a composite, every well-known kind once, six contracts with parts and fakes, scenarios across levels, and decisions of status derived and proposed. It is also the example of the build method [maike](https://github.com/wackazong/maike), which writes files like these from a source document.

## Why

The protocol has three pieces of knowledge that change for different reasons: the layout of a frame, the state of a session and the way bytes move over the line. Each is one unit, so a change to one changes one unit. The line is a composite, because reassembling frames from a byte stream is a calculation that is tested alone, while the port itself is the one place that talks to the outside world. Time comes from outside as a platform need, so every timeout is tested with a clock the test moves.

## Commands

```sh
alias unifold='python3 ../../docs/skills/unifold/scripts/unifold.py'
unifold check --strict
unifold show transport/serial
unifold model --json | head
```

## Read next

1. [frames](docs/references/frames.md): one contract with parts, examples and a fake that is the real implementation.
2. The generated [scenario open](docs/diagrams/scenario-open.md): a story drawn end to end across two levels.
3. [transport](transport/README.md): the composite adapter, and the decision that cut it.
