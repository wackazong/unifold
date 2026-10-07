# Glossary of alerts

The terms that have one fixed meaning inside `alerts` and that are not
defined above it. Terms from above are cited in [context](../context.md).

| Term | Meaning |
|---|---|
| Judging, evaluation | Comparing the judged values of one reading with the thresholds of its plant, to decide which alerts open and close. |
| Evaluation state | What judging the earlier readings of one sensor stick concluded: which alerts are open, the time of the last judged reading and the light of the last day. The process stores it; only the judging logic reads it. |
| Change | One entry in the result of an evaluation: "open" or "close" an alert for a quantity and a bound. |
| Cannot decide now | The result of an evaluation for which plant and thresholds could not be had. The reading is evaluated again later. |
| Lookup | Asking for the plant to which a sensor stick is attached, with owner and thresholds. Its answers are `attached`, `unattached` and `unavailable`. |
| Owed notification | The notification of a stored alert that the push service has not taken yet. The alert shows it as `pending`. |
| Delivery | The step that has owed notifications sent. It repeats until the outcome is `sent` or `failed`. |
| Process | The one running program of `alerts`. The other children are libraries built into it. |
