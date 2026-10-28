# serial

Writes a frame to the port and reads the port until a whole frame is there or the deadline has passed. The only unit that calls the port.

## Why

Every side effect of the line is here and nowhere else, so the rest of the program is tested with a port in memory and this unit alone runs its contract tests against the real port too. It keeps the bytes that arrived after the last frame and gives them to `framing` with the next read; it does not know what a frame looks like inside.
