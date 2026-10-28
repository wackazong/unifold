# framing

Takes the bytes kept from the last read and the bytes just read, and returns the complete frames in them and the bytes to keep. A pure calculation.

## Why

A byte stream can start in the middle of a frame, carry garbage, or hold two frames at once, and the port cannot be made to deliver these cases on demand. As a function over two byte lists, every case is one table row. The unit asks the codec whether the bytes at a magic byte are a frame; it does not know the layout itself.
