# slugline-command

Contract of `cli.slugline-command`: the command `slugline`. Notation: usage text.
Sources: the tests of `cli`

## Parts

### slugline

Kind: command

```text
slugline [OPTIONS] [TEXT]...
  -s, --separator CHAR   one ASCII symbol between words; default -
  -m, --max-len N        cut the slug after N characters
      --ascii            drop letters with diacritics instead of replacing them
  -h, --help             print the usage and exit with 0
  --                     everything after it is text
```

Pre: none.
Result: with `TEXT`, the arguments joined by one space as one slug, then a newline, on standard output. Without `TEXT`, one slug for each line of standard input, in the order of the lines. Exit code 0 when a slug was printed for every input.
Errors: exit 1 when standard input or output failed, with a message that starts with `slugline:`; exit 2 when an option is unknown or has no valid value, with the usage after the message.
Examples:

| Case | Input | Expected |
|---|---|---|
| arguments with diacritics | `slugline Crème brûlée` | `creme-brulee`, exit 0 |
| ascii only | `slugline --ascii Crème brûlée` | `crme-brle`, exit 0 |
| own separator | `slugline -s _ Hello World` | `hello_world`, exit 0 |
| lines of standard input | `printf 'a b\nc d\n' \| slugline` | `a-b` and `c-d` on two lines, exit 0 |
| bad separator | `slugline -s ab x` | exit 2, `slugline: the separator must be one ASCII symbol, not 'ab'` |

## Fake

Replays the examples: a test of the command runs the binary with the input of a row and compares output and exit code. Faults it can inject: none.
