# cli

`cli` is the command `slugline`.

## Provides

### `slug-cli`

`echo "Hello World" | slugline` prints `hello-world`.

- One line in, one line out, in the same order.
- Exit code 0 on success, 2 if the input is not valid UTF-8.
- `--separator` and `--max-len` set the separator and the longest slug.

## Needs

### `slugify`

One string in, one slug out, without input or output of its own.

### `transliteration`

Optional. Without it, characters outside ASCII are dropped from the slug.
