# <topic>

Contract of `<unit>.<capability>`, <what the connection is about, in a few words>. Notation: wit.
Sources: <where the facts come from, as text; or none>
Binding: <optional>
Carried by: <optional: [contract](other.md)>
Version: <optional>

## Use

<How a consumer uses the connection, in a few sentences: the order of the parts, what it does when a call fails, who may call when, and the rules that hold for every part. Without state: "Any part may be called at any time.">

<Where the order matters, a numbered list of the calls: the normal path first, then each failure that changes the state. Delete the list otherwise.>

1. `<part-name>`, then `<part-name>`.
2. When `<part-name>` fails with `<case>`, <what the consumer does next>.

## States

<Only where the connection has state; delete the section otherwise. The states a consumer can see or must respect. Every row names a part; a deadline is an event that the provider raises, or the error of the next call.>

Start: <state>.

| State | Part | Result | Next |
|---|---|---|---|
| <state> | `<part-name>` | ok | <state> |
| <state> | `<part-name>` | `<case>` | <state> |

## Parts

<In the order of use, one line each: what the part is for.>

- [<part-name>](<part-name>.md): <what it is for>
- [<type-name>](<type-name>.md): <what it holds>

## Fake

<What stands in for this contract in the tests of its consumers.>
