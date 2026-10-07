# AGENTS.md: notifier

This folder is a [youmedoc](https://youmedoc.example) unit.

## Why

Reaching an owner means dealing with a push service: its addressing, its
answers, its limits, and the wording of a message. None of that has to do
with why an alert opened. This unit keeps it in one place, so that a
change of provider or of wording touches nothing else.

The hard part is the word "once" in a world where every call can fail
half-way. `notifier` cannot know whether an earlier attempt for the same
alert got through, and it has no memory to ask. It therefore does not try
to send once. It makes sending twice harmless: every attempt for an alert
is the same message under the same collapse identifier
([0001](doc/decisions/0001-once-means-repeatable-with-a-collapse-identifier.md)).
Remembering that an attempt succeeded is left to the caller, who has a
place to store it.

What must stay true: `notify` is safe to call again, and `sent` is never
reported on a guess.

## Read next

1. [README.md](README.md): what the unit provides and needs
2. [doc/context.md](doc/context.md): what it inherits from above
3. [doc/diagrams/context.md](doc/diagrams/context.md): the unit in its
   surroundings
4. [doc/decisions/index.md](doc/decisions/index.md): decisions
5. [doc/references/notification.md](doc/references/notification.md): the
   function, the outcomes, the request to the push service, the texts

## Skills

| Skill | Use it when |
|---|---|
| [notifier-add-a-message](doc/skills/notifier-add-a-message/SKILL.md) | A quantity or bound has no text of its own yet, or a text shall change |

## Rules for work here

- The collapse identifier is the alert id and nothing else. Do not add an
  attempt number, a time or anything that differs between two calls for
  the same alert.
- Nothing in the message may differ between two calls for the same
  alert. No "sent at", no counters.
- When in doubt between `retry` and `failed`, return `retry`. A wrong
  `failed` loses a notification; a wrong `retry` costs a call.
- Never return `sent` after a timeout, even if the request probably
  arrived.
- Do not retry inside `notify`. One call is one attempt; the caller owns
  the schedule.
- Texts name the plant and the measured fact. They do not give advice
  beyond the obvious and do not mention the product.
