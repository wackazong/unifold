# <part-name>

Kind: <command | query | event | type>

```wit
<signature>
```

Pre: <what must hold before the call: the state it needs, by name>.
Result: <what holds afterwards, or what is returned>.
Errors: `<case>` when <condition>; or none.
Examples:

| Case | Input | Expected |
|---|---|---|
| <name of the case, once in this part> | `<call>` | <result, exact> |
