# <topic>

Contract of `<unit>.<capability>`, <what the connection is about, in a few words>. Notation: wit.
Sources: <where the facts come from, as text: proto §4; or none>

## Parts

### <part-name>

Kind: command

```wit
<name>: func(<argument>: <type>) -> result<<type>, <error-type>>;
```

Pre: <what must hold before the call: state, call order, ranges, by constant name>.
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

<One of: "Replays the examples. Any other call fails with `unexpected-call`. Faults it can inject: none." Or the simplified behaviour and the faults, for a need of the root: "A port in memory: ... Faults it can inject: ...". Or, for a logic provider: "The real implementation: <why a replay fake would be worse>.">
