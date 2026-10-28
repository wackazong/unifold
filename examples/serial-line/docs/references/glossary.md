# Glossary

The terms of the protocol as the code uses them. One row per term, so that a unit can cite one.

| Term | Meaning |
|---|---|
| host | The side that opens the session: this program. |
| device | The side that answers over the line. It never opens a session. |
| session | The state between a successful open and a close. Data travels only inside a session. |
| frame | The unit of transmission on the line: magic byte, length, payload, CRC. |
| payload | The bytes a frame carries. The first byte is the operation code. |
| ACK | A frame whose payload is the operation code of the request with the top bit set. |
| magic byte | The byte `MAGIC_BYTE` that starts every frame. |
