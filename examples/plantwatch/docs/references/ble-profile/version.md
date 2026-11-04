# version

Kind: type

```text
version: major (1 byte) . minor (1 byte); both in Info, the major number alone in the advertising data
```

The profile has a version `major.minor`. A sensor stick reports both numbers in the Info characteristic and the major number in its advertising data.

Within one major version, a later minor version may only:

- add a characteristic to the service,
- add an op code or a result code,
- add bytes at the end of a characteristic value or of an op code's parameters,
- give a meaning to a reserved bit,
- add a quantity to the record, as the [reading schema](../reading-schema.md) allows.

Within one major version, no version removes anything, moves a field, or changes the meaning, size or scaling of an existing field.

What each side does so that this works:

| Side | Rule |
|---|---|
| Central | Ignores characteristics, trailing bytes, flag bits and record fields it does not know |
| Central | Treats a result code it does not know as a failure of that request |
| Central | Works with a sensor stick whose value is shorter than it knows: a missing trailing field counts as absent or 0 |
| Central | Does not write to a sensor stick whose major version is higher than the highest it implements |
| Sensor stick | Answers an op code it does not know with the result `op-code-not-supported` |
| Sensor stick | Accepts parameters that are longer than it knows and ignores the extra bytes |
