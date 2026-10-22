# slugline-command

The contract of `slugline-command`: the command `slugline`.

## Usage

```text
slugline [OPTIONS] [TEXT]...
```

- With `TEXT`, prints the arguments joined by one space as one slug, then a newline.
- Without `TEXT`, prints one slug for each line of standard input.
- `-s`, `--separator CHAR`: one ASCII symbol between words. Default `-`.
- `-m`, `--max-len N`: cut the slug after `N` characters.
- `--ascii`: drop letters with diacritics instead of replacing them.
- `-h`, `--help`: print the usage and exit with 0.
- `--`: everything after it is text.

## Exit codes

| Code | When |
|---|---|
| 0 | A slug was printed for every input |
| 1 | Standard input or output failed; the message starts with `slugline:` |
| 2 | An option is unknown or has no valid value; the usage follows the message |

## Examples

| Command | Output |
|---|---|
| `slugline Crème brûlée` | `creme-brulee` |
| `slugline --ascii Crème brûlée` | `crme-brle` |
| `slugline -s _ Hello World` | `hello_world` |
| `printf 'a b\nc d\n' \| slugline` | `a-b` and `c-d` on two lines |
| `slugline -s ab x` | exit 2, `slugline: the separator must be one ASCII symbol, not 'ab'` |
