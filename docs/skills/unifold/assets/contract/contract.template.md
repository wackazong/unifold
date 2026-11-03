# <topic>

Contract of `<unit>.<capability>`, <what the connection is about, in a few words>. Notation: wit.
Sources: <where the facts come from, as text: proto §4; or none. Never a decision.>

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

### <part-name>

Kind: command

```wit
<name>: func(<argument>: <type>) -> result<<type>, <error-type>>;
```

Pre: <what must hold before the call: the state it needs, ranges by constant name>.
Result: <what holds afterwards, or what is returned>.
Errors: `<case>` when <condition>; or none.
Examples:

| Case | Input | Expected |
|---|---|---|
| <name of the case, and the source where it gives the vector> | `<call>` | <result, exact> |
| <one over the limit> | <input> | `<error case>` |

### <type-name>

Kind: type

```wit
record <type-name> { <field>: <type> }
```

| Field | Meaning |
|---|---|
| <field> | <what it holds> |

### <error-type>

Kind: type

```wit
variant <error-type> { <case>, <other-case> }
```

## Fake

<One of: "Replays the examples. Any other call fails with `unexpected-call`. Faults it can inject: none." Or the simplified behaviour and the faults, for a need of the root: "A port in memory: ... Faults it can inject: ...". Or, for a logic provider or a capability of the root: "The real implementation: <why a replay fake would be worse>.">
