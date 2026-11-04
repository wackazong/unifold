# notifier

`notifier` is an adapter that tells an owner about an opened alert. Its caller sees a plain function. Behind it, `notifier` words the message, hands it to a push service addressed to the owner, and reports how that went. It stores nothing. It is built so that a caller that is unsure whether a notification went out can simply ask again.

## Why

What this unit hides is how one notification per alert is achieved towards the push service ([0001](docs/decisions/0001-once-means-repeatable-with-a-collapse-identifier.md)). Reaching an owner means dealing with a push service: its addressing, its answers, its limits, and the wording of a message. None of that has to do with why an alert opened. This unit keeps it in one place. It changes when the push provider or the wording of a message changes, and such a change touches nothing else.

The hard part is the word "once" in a world where every call can fail half-way. `notifier` cannot know whether an earlier attempt for the same alert got through, and it has no memory to ask. It therefore does not try to send once. It makes sending twice harmless: every attempt for an alert is the same message under the same collapse identifier ([0001](docs/decisions/0001-once-means-repeatable-with-a-collapse-identifier.md)). Remembering that an attempt succeeded is left to the caller, who has a place to store it.

What must stay true: `notify` is safe to call again, and `sent` is never reported on a guess.

## Read next

1. [notification](../docs/references/notification.md): the function, the outcomes, the request to the push service, the texts
2. [docs/explanation/context.md](docs/explanation/context.md): what the unit inherits
3. [Decisions](docs/decisions/index.md)
